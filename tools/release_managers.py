import argparse
from ruamel.yaml import YAML
from packaging.version import Version


class Release:
    def __init__(self, version: Version, type, managers, date=None):
        self.version = version
        self.date = date
        self.type = type
        self.managers = managers
        # The release was done (it has a date) or it was NOT done yet (it has no date)
        self.done = date is not None

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

    def update_queue(self, managers, kind):
        if self.type == "major":
            pass  # TODO continue from here

    def add_release(self, release_data):
        self.history.update(release_data)
        self.update_queue(release_data["managers"])

    def team(self):
        ret = set()
        for people_in_queue in self.data["queue"].values():
            ret.update(people_in_queue)
        return ret

    def get_release(self, version: Version):
        release = self.find_release(version)
        if release:
            return release
        release_type = "first" if self.is_first(version) else "followup"
        self.next_in_queue(release_type, 2)
        return Release(version, type=release_type, managers=self.next_in_queue(release_type, 2))

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

    def next_in_queue(self, queue_name, n):
        """
        Returns a list of the n next user in the queue with name queue_name
        """
        return self.data["queue"][queue_name][:n]


def who_command(args, db):
    print(db.get_release(args.version))


def release_command(args, db):
    # TODO
    version = args.version
    release_manager = args.by  # if version in db.history:
    #     print(f'{version} was already released by {db.history[version]["managers"]}')
    #     return
    #
    # new_release = Release(args.version, release_managers=args.rm)
    # print("new release", new_release.to_yaml_dict())
    # db.add_release(new_release)
    # db.refresh_file()
    pass


db = ReleaseManagerYamlFile("release_managers.yaml")
parser = argparse.ArgumentParser()

"""who --version 1.4.1   (who's releasing coming 1.4.1)"""
subparsers = parser.add_subparsers()

parser_who = subparsers.add_parser("who", help="who should/did release <version>?")
parser_who.set_defaults(func=who_command)
parser_who.add_argument("-v", "--version", metavar="<version>", help="qiskit version", type=Version)

"""release --version 1.4.1  --by eliarbel --by 1ucian0    (record a release by release master/s)"""
parser_release = subparsers.add_parser(
    "release", help="record that <version> was released by <release_manager>"
)
parser_release.set_defaults(func=release_command)
parser_release.add_argument(
    "-v", "--version", metavar="<version>", help="qiskit version", type=Version
)
parser_release.add_argument(
    "-b",
    "--by",
    nargs="+",
    action="extend",
    metavar="person",
    choices=db.team(),
    help=f"release manager (one or many. First, the main release manager).",
)

args = parser.parse_args()

db = ReleaseManagerYamlFile("release_managers.yaml")

args.func(args, db)
