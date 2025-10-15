import argparse
import sys

from ruamel.yaml import YAML
from dateutil.parser import parse
from datetime import datetime, timedelta
from packaging.version import Version
from os import path
import requests

gh_team_directory = "Qiskit/teams/terra-release"


class Release:
    def __init__(self, version: Version, type, managers=None, date=None):
        self.version = version
        self.date = date
        self.type = type
        self.managers = managers

    @property
    def done(self):
        # The release was done (it has a date) or it was NOT done yet (it has no date)
        return self.date is not None

    def __str__(self):
        ret = ""
        if self.done:
            ret += f"{self.date}: {'/'.join(self.managers)} released {self.version}"
        else:
            ret += self.managers[0]
            if len(self.managers) > 1:
                ret += f" (followed by {'/'.join(self.managers[1:])})"
            ret += f" is next in the queue to release {self.version}"
        if self.type == "followup":
            ret += f" as a follow-up in the {self.version.major}.{self.version.minor} series."
        else:
            ret += f" initiating the {self.version.major}.{self.version.minor} series."
        return ret

    def done_by(self, managers):
        response = requests.get(f"https://pypi.org/pypi/qiskit/{self.version}/json")
        data = response.json()
        date = max([datetime.fromisoformat(u["upload_time_iso_8601"]) for u in data["urls"]])
        self.managers = managers
        self.date = date.strftime("%b %d, %Y")


class ReleaseManagerYamlFile:
    def __init__(self, filename):
        self.filename = filename
        self.yaml = YAML()
        self._data = None

    def refresh_file(self):
        with open(self.filename, "w") as file:
            self.yaml.dump(self._data, file)

    def load(self):
        with open(self.filename, "r") as file:
            self._data = self.yaml.load(file)
        return self._data

    @property
    def data(self):
        return self._data or self.load()

    @property
    def history(self):
        return self.data["history"]

    def update_queue(self, release):
        if not release.done:
            sys.exit("attempt to update the queue with a release that it was not done")
        for release_manager in reversed(release.managers):
            self.to_the_end_of_the_queue("followup", release_manager)
            if release.type == "first":
                self.to_the_end_of_the_queue("first", release_manager)

    def add_release(self, release):
        self.history.insert(
            pos=0,
            key=str(release.version),
            value={"date": release.date, "type": release.type, "managers": release.managers},
        )
        self.update_queue(release)

    def team(self):
        ret = set()
        for people_in_queue in self.data["queue"].values():
            ret.update(people_in_queue)
        return ret

    def get_release(self, version: Version, include_potential_rm=True):
        release = self.find_release(version)
        if release:
            return release
        release_type = "first" if self.is_first(version) else "followup"
        if include_potential_rm:
            return Release(version, type=release_type, managers=self.next_in_queue(release_type, 2))
        else:
            return Release(version, type=release_type)

    def find_release(self, version):
        str_version = str(version)
        if str_version in self.history:
            return Release(version, **self.history[str_version])

    def is_first(self, version: Version):
        major_minor_versions = set()
        for v in self.history.keys():
            V = Version(v)
            major_minor_versions.add((V.major, V.minor))
        return (version.major, version.minor) not in major_minor_versions

    def next_in_queue(self, queue_name, n, exclude_rules=None):
        """
        Returns a list of the n next user in the queue with name queue_name

        exclude_rules:
            (<queue_name>, <positions>)
            ('first', 2): Default for queue_name==followup. If a person is first or second in the 'first' queue
            ('history', <amount of days, -1 never>)
            ('released', -1): Default for queue_name==first. If the person never did a release
            ('released', 120): Default for all situations. If the person did a release in the last 120 days
        """
        if exclude_rules is None:
            exclude_rules = [("released", 120)]
            if queue_name == "followup":
                exclude_rules.append(("first", 2))
            if queue_name == "first":
                exclude_rules.append(("released", -1))

        def matches_rule(u, r):
            category, arg = r
            prelude = f"{user} excluded:"
            if category == "released":
                for release in self.history.values():
                    if u in release["managers"]:
                        if arg == -1:
                            print(f"{prelude} user did not released before")
                            return True
                        else:
                            if datetime.today() - timedelta(days=arg) < parse(release["date"]):
                                print(
                                    f"{prelude} user was release manager less than {arg} days ago"
                                )
                                return True
            else:
                if u in self.data["queue"][category][:arg]:
                    print(f"{prelude} user is in the first {arg} places in the '{category}' queue")
                    return True
            return False

        retlist = list()
        for user in self.data["queue"][queue_name]:
            for exclude_rule in exclude_rules:
                if matches_rule(user, exclude_rule):
                    break
            else:
                retlist.append(user)
                if len(retlist) >= n:
                    return retlist

    def to_the_end_of_the_queue(self, queue, release_manager):
        self._data["queue"][queue].remove(release_manager)
        self._data["queue"][queue].append(release_manager)


def who_command(args, db):
    print(db.get_release(args.version))


def release_command(args, db):
    release_managers = args.release_managers
    release = db.get_release(args.version, include_potential_rm=False)
    if release.done:
        print(f"{release.version} was already released on {release.date}")
        return
    release.done_by(release_managers)
    db.add_release(release)
    db.refresh_file()


class update_team_action(argparse.Action):
    def __init__(self, option_strings, dest, gh_team_directory, db, **kwargs):
        self._gh_team_directory = gh_team_directory
        self._db = db
        return super().__init__(option_strings, dest, nargs=0, default=argparse.SUPPRESS, **kwargs)

    def __call__(self, parser, namespace, values, option_string, **kwargs):
        raise NotImplementedError(
            f"TODO: fetch {self._gh_team_directory} and update {self._db.filename}"
        )
        parser.exit()


db = ReleaseManagerYamlFile(path.join(path.dirname(__file__), "release_managers.yaml"))
parser = argparse.ArgumentParser()

"release_managers.py -ut  # updates the release manager team"
parser.add_argument(
    "-ut",
    "--update-team",
    action=update_team_action,
    gh_team_directory=gh_team_directory,
    db=db,
    help=f"fetches {gh_team_directory} and update the release managers",
)

parser.add_argument(dest="version", metavar="<version>", help="qiskit version", type=Version)
"""
release_managers.py 1.4.1 who  # who's releasing coming 1.4.1
release_managers.py 11.0 who   # who's next in line to be the release manager for major 11.0 release
release_managers.py 1.4.99 who # who's next in line to be the release manager for patch 1.4.99 release
"""
subparsers = parser.add_subparsers()

parser_who = subparsers.add_parser("who", help="who should/did release <version>?")
parser_who.set_defaults(func=who_command)

"""
release_managers.py 3.0 release -h  # help on how to record the release of 3.0
release_managers.py 1.4.1 release eliarbel 1ucian0  # record a release by release managers/s)
"""
parser_release = subparsers.add_parser(
    "release", help="record that <version> was released by <release_manager>"
)
parser_release.set_defaults(func=release_command)
parser_release.add_argument(
    "release_managers",
    nargs="+",
    action="extend",
    metavar="person",
    choices=db.team(),
    help=f"release manager (one or many. First, the main release manager).",
)

args = parser.parse_args()

args.func(args, db)
