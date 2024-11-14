import curses
import random

def main(stdscr):
    # Initialize the screen
    curses.curs_set(0)          # Hide the cursor
    stdscr.nodelay(1)           # Don't block I/O calls
    stdscr.timeout(100)         # Refresh screen every 100 ms

    # Get screen dimensions
    sh, sw = stdscr.getmaxyx()  # sh = screen height, sw = screen width

    # Initial snake position and body
    snk_x = sw // 4
    snk_y = sh // 2
    snake = [
        [snk_y, snk_x],
        [snk_y, snk_x - 1],
        [snk_y, snk_x - 2],
    ]

    # Place the first food item
    food = [sh // 2, sw // 2]
    stdscr.addch(food[0], food[1], curses.ACS_PI)

    # Start moving right
    key = curses.KEY_RIGHT

    # Initialize the score
    score = 0

    while True:
        # Display the score at the top of the screen
        stdscr.addstr(0, 0, f'Score: {score}')

        next_key = stdscr.getch()
        key = key if next_key == -1 else next_key

        # Calculate the new head position
        y = snake[0][0]
        x = snake[0][1]
        if key == curses.KEY_DOWN:
            y += 1
        elif key == curses.KEY_UP:
            y -= 1
        elif key == curses.KEY_LEFT:
            x -= 1
        elif key == curses.KEY_RIGHT:
            x += 1

        # Insert the new head position
        snake.insert(0, [y, x])

        # Check for collision with borders or self
        if (
            y in [0, sh]
            or x in [0, sw]
            or [y, x] in snake[1:]
        ):
            msg = "Game Over!"
            stdscr.addstr(sh // 2, sw // 2 - len(msg) // 2, msg)
            stdscr.nodelay(0)
            stdscr.getch()
            break

        # Check if snake has found the food
        if [y, x] == food:
            # Increase the score
            score += 1
            # Place new food
            while True:
                new_food = [
                    random.randint(1, sh - 2),
                    random.randint(1, sw - 2),
                ]
                if new_food not in snake:
                    food = new_food
                    break
            stdscr.addch(food[0], food[1], curses.ACS_PI)
        else:
            # Remove the tail segment
            tail = snake.pop()
            stdscr.addch(tail[0], tail[1], ' ')

        # Draw the head of the snake
        stdscr.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)

curses.wrapper(main)
