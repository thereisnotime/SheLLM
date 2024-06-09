# SheLLM

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Tests

Test following cases:

- [ ] Test if it works while in SSH and if remote server will save history.
- [ ] Test how long history can be used/contextualized.
- [ ] Test if it works with different shells.
- [ ] Test if it handles errors.
- [ ] Test in tmux.
- [ ] Test in screen.

## Roadmap

- [ ] Add configuration support (LLM, token, history size, trigger chars, execute command without confirmation).
- [ ] Add wrapper for screen (auto start and stop).
- [ ] Remove questions from history.
- [ ] Proper handling of error exits.
