# Session audio kit

session audio kit is a tool to mix, merge, transcribe, and generally format your ttrpg session recordings from software such as [craig](https://craig.chat/home/)

## Installation

clone the repo then use the package manager [pip](https://pip.pypa.io/en/stable/) to install session audio kit.

<!-- TODO: add proper url -->

## Usage

<!-- TODO: add output an stuff? -->

```bash
python -m session_audio_kit -o "session_recordings/" -r "session_recordings/raw/" -n "session1!" -a "session-recording-part-1.zip" "session-recording-part2.gzip"
```

## Options

### -o --output

directory to place the final audio file after all processing

### -r --raw_output

directory to store the audio files before processing as extracted from archive file(s)

### -a --archive

archive (zip,gzip) files to be processed

note: archive files should be formatted with each speaker in a seperate flac file

### -n --name \*

name of the session

### -c --config

path to optional config file

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[GPLV3](https://www.gnu.org/licenses/gpl-3.0.en.html)
