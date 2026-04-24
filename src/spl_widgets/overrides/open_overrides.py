from subprocess import run
import pkg_resources

def main():
    overrides_fp = pkg_resources.resource_filename("spl_widgets", "overrides/tuner_overrides.py")
    run(["open", overrides_fp])