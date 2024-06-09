<p align="center"><img align="center" width="280" src="./assets/icon.png"/></p>
<h3 align="center">Let the AI  in your terminal </h3>
<hr>

<h3 align="center">🤖 Powered by [INSERT LLM HERE]) 🤖</h3>

<h3>NOTE: This is a PoC in very, very early stage of development (but it works). Help is most welcome!<h3>

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=bash,linux,py" />
  </a>
</p>

# SheLLM [![stability][0]][1]

A PoC for a shell wrapper that integrates LLM model(s) for command suggestions and questions with context awareness.
It can also execute commands and provide suggestions based on the context.

> It is in very, very early stage of development so expect bugs and issues.

## Table of Contents

- [SheLLM \[!\[stability\]\[0\]\]\[1\]](#shellm-stability01)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Motivation](#motivation)
  - [Setup and Usage](#setup-and-usage)
  - [Tests](#tests)
  - [Known Issues](#known-issues)
  - [Roadmap](#roadmap)
  - [Contribution](#contribution)
  - [License](#license)
  - [Acknowledgements](#acknowledgements)

## Features

- Shell wrapper that can provide suggestions (and execute commands).
- Knows about previous commands and their output (context awareness).
- Confirmation before executing commands.
- ChatGPT integration.
- Groq integration.

## Motivation

The motivation behind SheLLM is to provide a more intelligent shell that can help users with suggestions and context-awareness. The idea is to use a language model to understand the context of the commands and provide suggestions based on the context.

## Setup and Usage

Pre-requisites:

```bash
# - Python 3.12 + python3.12-venv (maybe lower versions will work too)
# - Groq or OpenAI API key
cp .env.example .env # Update .env with your configuration.
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Usage:

```bash
python3 main.py --llm-api=openai
# or
python3 main.py --llm-api=groq
```

## Tests

Test following cases/scenarios:

- [x] Test if it works while in an SSH session and if remote server will save prompt history. - works, prompt not saved.
- [ ] Test how long history can be used/contextualized.
- [ ] Test if it works with different shells.
- [ ] Test if it handles errors.
- [ ] Test in tmux.
- [ ] Test in screen.
- [ ] Test if it will work better outside of venv when multiplexed.
- [ ] Test context handling.

## Known Issues

The following are the current known issues with SheLLM:

- [ ] SheLLM does not like an empty command.
- [ ] SheLLM does not handle SSH stream properly (could be better).
- [ ] SheLLM does not handle error exits properly.
- [ ] SheLLM does not handle streaming output properly.
- [ ] SheLLM does not handle TAB completion for commands.
- [ ] SheLLM breaks scroll in the terminal after it crashes.
- [ ] SheLLM does not handle ALT/CTRL cursor movement shortcuts.
- [ ] SheLLM's context should take the last output with higher priority and not the previous commands.

## Roadmap

Feel free to contribute to the roadmap by creating issues or pull requests with new features or improvements.

- [x] Add support for ChatGPT.
- [x] Add Groq support.
- [ ] Add support for self-hosted LLM models.
- [ ] Improve code structure and quality (e.g. add type hints, docstrings, etc.).
- [ ] Add a proper logging mechanism.
- [ ] Add context size warnings and automatic context cleanup.
- [ ] Proper handling of error exits.
- [ ] Build PyPI package.
- [ ] Improve repository structure.
- [ ] Add env/config validation on load.
- [ ] Add Jinja2 support for prompt customization.
- [ ] Handle proper stream disconnects (SSH/top etc.).
- [ ] Add a mechanism to detect errors after commands execution and ask to solve them.
- [ ] Add configuration support (LLM type, LLM model config per command type, token, history size, trigger chars, execute command without confirmation).
- [ ] Add wrapper for screen (auto start and stop).
- [ ] Add `fzf` support with suggestion mode for commands + shortcut to return to previous choice.
- [x] Remove SheLLM prompts from history (intercept).
- [ ] Add detailed SheLLM history (with timestamps) for each session.
- [ ] Add local logging for full terminal context for future embeddings optimization.
- [ ] Do not approve PRs from John Connor 🤖.
- [ ] Add mechanism to handle streaming output (e.g. tail -f, top, etc.).
- [ ] Add TAB completion for commands.
- [ ] Add support for PowerShell.

## Contribution

Feel free to contribute to SheLLM by creating issues or pull requests.

## License

Check the [LICENSE](LICENSE) file for more information.

## Acknowledgements

- [OpenAI](https://openai.com) for providing their Python library and nice API.
- [Groq](https://groq.com) for providing their Python library and nice API.
- [colorama](https://pypi.org/project/colorama/) for providing an easy way to color the terminal output.
- [python-dotenv](https://pypi.org/project/python-dotenv/) for providing an easy way to load environment variables from `.env` file.
- [click](https://pypi.org/project/click/) for providing an easy way to create command-line interfaces.
