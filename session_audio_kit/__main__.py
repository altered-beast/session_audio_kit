import configparser
import argparse
import shutil
import os.path as path
import glob

import ffmpeg


class Options:
    def __init__(self):

        self.args = self.parse_cli_args()

        if self.args.config is not None:
            self.config = self._read_config()
        else:
            self.config = None

        self.archives = self.args.archive
        self.name: str = self.args.name
        self.config_path: str = self.args.config

    def parse_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-o", "--output", nargs="?", help="path to output the final recording to "
        )
        parser.add_argument(
            "-r",
            "--raw_output",
            nargs="?",
            help="path to place raw files after decompression(sorted by archive file)",
        )
        parser.add_argument(
            "-a",
            "--archive",
            nargs="+",
            required=True,
            help="archive file(s) to process",
        )
        parser.add_argument(
            "-c", "--config", nargs="?", help="optional configuration file path"
        )
        parser.add_argument(
            "-n", "--name", required=True, help="name of the final recording"
        )
        return parser.parse_args()

    def _read_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        return config

    @property
    def raw_dir(self):
        return self.get_from_config_or_args("raw_output")

    @property
    def save_path(self):
        return self.get_from_config_or_args("output")

    def get_from_config_or_args(self, value):
        if self.config is not None:

            if self.config["directories"][value]:
                return self.config["directories"][value]
        else:
            return vars(self.args)[value]


class Recording:
    def __init__(self, track_path, format=".flac"):
        self.path = track_path
        self.format = format

        self.tracks: list = glob.glob(f"{track_path}/*{format}")
        self.mixed_track: path.abspath = None

    def mix(self):
        output = f"{self.path}/mixed{self.format}"
        inputs = []
        # convert flac files to ffmpeg inputs
        for track in self.tracks:

            inputs.append(ffmpeg.input(track))

        # mix together all inputs using amix https://ffmpeg.org/ffmpeg-filters.html#amix
        self.mixed_track = output

        return (
            ffmpeg.filter(inputs, "amix", inputs=len(inputs), normalize=False)
            .output(output)
            .run_async(pipe_stdout=True, pipe_stdin=True)
        )


class Session:
    def __init__(self, options: Options):
        self.recordings: list[Recording] = []
        self.options: Options = options
        self._init_recordings()

    def _init_recordings(self):
        # unpack all archives into raw_dir in separate directories
        for i, archive in enumerate(self.options.archives):
            save_path = path.join(self.options.raw_dir, self.options.name, str(i))

            shutil.unpack_archive(archive, save_path)
            # create recordings for each directory
            self.recordings.append(Recording(save_path))

    def mix_all(self):
        # run .mix() on all recordings asynchronously
        futures = []
        rec: Recording
        for rec in self.recordings:

            futures.append(rec.mix())
        # wait for mixing to finish
        for f in futures:
            f.wait()

    def concat_and_export(self):
        output = path.join(self.options.save_path, self.options.name + ".flac")
        if len(self.recordings) > 1:
            inputs = []

            rec: Recording
            # make ffmpeg inputs from files
            for rec in self.recordings:
                inputs.append(ffmpeg.input(rec.mixed_track))
            # concatenate the inputs and output to final file  https://ffmpeg.org/ffmpeg-filters.html#concat
            (ffmpeg.concat(*inputs, v=0, a=1).output(output).run())
        else:
            shutil.move(self.recordings[0].mixed_track, output)


if __name__ == "__main__":
    options = Options()
    session = Session(options)
    session.mix_all()
    session.concat_and_export()
