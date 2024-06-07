# Vim as a Python IDE

**Language Help**
- Code Navigation - go to definition, references, type definition, implementation
- Linting & Diagnostics - static type checking, errors, warnings
- Intellisense auto-complete - recommend variables in scope, object methods, function parameters, 
- Display docs - popup documentation of classes and methods
- Auto formatting - Automatically format according to standardized style guides
- Visual debugging - (as opposed to command line) debug with variables, call stack, and step through code etc. 
- Pythonic Folding and indentation - Fold classes, functions

**General goodness**
- Fuzzy file (name) search - open files by partially matching with file names
- Fuzzy full-text search - search for arbitrary patterns in files
- File tree - visualize the directory tree and open files
- Easy git operation - list unstaged files, compare diffs, stage files with one keystroke

## Setup
### Install prerequisites
#### Vim with Python 3 support


### Installing vim plugins and configuration
Clone the repository and run `bash setup.sh`.
*It will overwrite your .vimrc, but save the old one as .vimrc.backup .* 
This is done to automate installation while avoiding a clash with the previous setup. 


It uses [Plug](https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim) as the plugin manager 
and has a separate vimrc file with keybindings/configurations corresponding to each plugin that you can customize. 
You can even exclude the plugin and the corresponding vimrc file if you don't want to use it. 
If you fork this repo, and push your customizations, you can easily setup vim anywhere 
(e.g. friend's computer, servers). The setup script will automatically install the vim plugins and coc extensions.

For full text search, I like using ripgrep (rg), a fast regex search written in Rust, 
for full text search, (exposed as `:Rg` via fzf). 
To install ripgrep on your system follow these [installation instructions](https://github.com/BurntSushi/ripgrep#installation).

The installation script adds the default keybindings for each package (for e.g. `coc.vimrc`).

### Color scheme
Most default terminals come with just 16 colors but provide the specify true colors corresponding to them. 
Most color schemes for vim however, use truecolors and only work properly with GUI vim (Gvim, NeoVIM etc.). 
If they use colors outside the 16 defined for the terminal, then it leads to unreadable mess. 
Many color schemes however provide the ability to use just 16 colors and provide a mapping from these 16 
colors to truecolors, the caveat being that you need to configure your terminal (emulator). 

#### For solarized terminal color scheme 
To get set the terminal colors to solarized, `git clone https://github.com/tomislav/osx-terminal.app-colors-solarized.git` 
and import a `.terminal` file into preferences. 
The `setup.sh` script will take care of setting the color scheme and activating it. 


## Plugins (a.k.a. what's being installed)
We will use the following plugins 
- [CoC](https://github.com/neoclide/coc.nvim) to get modern code help from a language server (over LSP) like Code navigation, linting, autocomplete, docs, formatting
- [Vimspector](https://github.com/puremourning/vimspector) for visual debugging
- [SimpylFold](https://github.com/tmhedberg/SimpylFold) for python specific code folding for vim, [FastFold](https://github.com/Konfekt/FastFold) to speed up folding
- [IndentPython](https://www.vim.org/scripts/script.php?script_id=974) to follow PEP 8 while indenting python code
- [CtrlP](https://github.com/kien/ctrlp.vim) for fuzzy file, buffer, mru, tag, etc finding
- [FzF](https://github.com/junegunn/fzf) for fuzzy full-text search with ripgrep
- [Fugitive](https://github.com/tpope/vim-fugitive) for git operation
- [NerdTree](https://github.com/preservim/nerdtree) a tree (file) explorer

                                                                *** Happy coding! ***
![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](https://myoctocat.com/assets/images/base-octocat.svg)