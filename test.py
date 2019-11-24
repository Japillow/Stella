# import curses
# import curses.panel
# screen = curses.initscr()
# curses.start_color()
# curses.noecho()
# curses.curs_set(1)
# screen.keypad(1)
# curses.cbreak()
# height, width = screen.getmaxyx()

# window = curses.newwin(1, 1, 1, 1)
# window2 = curses.newwin(height - 2, (width // 2) - 10, 1, width // 2 + 1)

# left_panel = curses.panel.new_panel(window)
# right_panel = curses.panel.new_panel(window2)

# window.border('|', '|', '-', '-', '+', '+', '+', '+')
# window2.border('|', '|', '-', '-', '+', '+', '+', '+')

# curses.panel.update_panels()
# curses.doupdate()

# running = True
# x = 0
# while (running):
#     height, width = screen.getmaxyx()
#     k = window.getch()
#     if k == curses.KEY_RESIZE:
#         window2.erase()
#         window.erase()
#         h, w = screen.getmaxyx()
#         window2.resize(height - 2, (width / 2) - 10)
#         window.resize(height - 2, (width / 2) - 10)
#         left_panel.replace(window)
#         right_panel.replace(window2)
#         left_panel.move(0, 0)
#         right_panel.move(0, width / 2)
#         window2.border('|', '|', '-', '-', '+', '+', '+', '+')
#         window.border('|', '|', '-', '-', '+', '+', '+', '+')
#     if k == ord('q') or x >= 10:
#         running = False
#         curses.endwin()
#     curses.panel.update_panels()
#     curses.doupdate()

import curses

screen = curses.initscr()
window = curses.newwin(100, 100)
window.addstr(3, 1, "Hello")
window.refresh()
a = window.getch()
