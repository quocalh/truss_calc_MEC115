this comes with the virtual environment setup, pls follow these:
objectives:
  - to activate the virtual environment first
  - run  
  - to deactivate them afterward

to create one, in the current directory:
  -> python  -m venv ./.venv

now that you have created one, to actually use them:
  -> cd .venv
  -> cd bin
you can even use "ls -a" to check the component insidee the working environment

to activate them:
  -> source activate

to check if you are in the virtual environment:
  -> which python python3 pip
  for example, my git repo directory (the one i want to work with): /home/mouse/Projects/py/pg_testing
    when i execute: ~/home/mouse/Projects/py/pg_testing $ which python python3 pip
      it should be:
        /home/mouse/Projects/py/pg_testing/.venv/bin/python3
        /home/mouse/Projects/py/pg_testing/.venv/bin/python
        /home/mouse/Projects/py/pg_testing/.venv/bin/pip
  that's mean you are in the working environment


to deactivate, simply go back to the directory and deactivate it:
  deactivate -- you can be anywhere in the directory

nvim - get path
  :echo expand('%:p')

-- for pygame
https://github.com/pygame/pygame/issues/4525#issuecomment-3961452008
before install, considering type this
  export PYGAME_DETECT_AVX2=1
  pip install pygame

-- idk (to handle an LSP)
The health checker is your friend
-> the nvim ":healthcheck" go to the lsp  section to see the info
The lazy/nvim-lspconfig is your god
-> every info must be aligned with that source

some of the yellow warnings or maybe just pyflakes tweaking yk dw, just config to block it
