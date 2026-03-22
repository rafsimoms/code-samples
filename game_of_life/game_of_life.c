#include <ncurses.h>
#include <stdio.h>
#include <stdlib.h>

#define MIN_SPEED 10000
#define MAX_SPEED 200000
#define SPEED_STEP 10000

void fill_zero_matrix(int **matrix);
void output(int **matrix);
void counter(int **matrix, int **count_matrix);
void changing(int **matrix, int **count_matrix);
void load_from_file(int **matrix, char *filename);
void draw_ui_info(int speed);
void handle_user_input(int *speed, int *running);
void start_input(char *choice);

int main() {
    initscr();
    cbreak();
    noecho();
    curs_set(0);
    keypad(stdscr, TRUE);
    nodelay(stdscr, TRUE);
    int **matrix = malloc(25 * sizeof(int *));
    for (int i = 0; i < 25; ++i) {
        matrix[i] = malloc(80 * sizeof(int));
    }
    int **count_matrix = malloc(25 * sizeof(int *));
    for (int i = 0; i < 25; ++i) {
        count_matrix[i] = malloc(80 * sizeof(int));
    }
    fill_zero_matrix(count_matrix);
    char choice = '0';
    start_input(&choice);
    char *files[] = {"pond.txt", "eight.txt", "ship.txt", "diff.txt", "pulsar.txt"};
    load_from_file(matrix, files[choice - '1']);
    int speed = 100000;
    int running = 1;
    while (running) {
        counter(matrix, count_matrix);
        changing(matrix, count_matrix);
        output(matrix);
        draw_ui_info(speed);
        handle_user_input(&speed, &running);
        refresh();
        napms(speed / 1000);
    }
    for (int i = 0; i < 25; ++i) {
        free(count_matrix[i]);
        free(matrix[i]);
    }
    free(count_matrix);
    free(matrix);
    endwin();
}

void start_input(char *choice) {
    printw("Choose a configuration file (1-5):\n");
    printw("1. Pond\n2. Figure 8\n3. Ship\n4. Different figures\n5. Pulsar\n");
    refresh();
    while (*choice < '1' || *choice > '5') {
        *choice = getch();
    }
}

void output(int **matrix) {
    clear();
    for (int i = 0; i < 25; ++i) {
        for (int j = 0; j < 80; ++j) {
            if (matrix[i][j] == 0) {
                mvprintw(i, j, ".");
            } else {
                mvprintw(i, j, "0");
            }
        }
    }
}

void fill_zero_matrix(int **matrix) {
    for (int i = 0; i < 25; ++i) {
        for (int j = 0; j < 80; ++j) {
            matrix[i][j] = 0;
        }
    }
}

void counter(int **matrix, int **count_matrix) {
    for (int i = 0; i < 25; ++i) {
        for (int j = 0; j < 80; ++j) {
            int x_min = j - 1;
            int x_max = j + 1;
            int y_min = i - 1;
            int y_max = i + 1;
            if (x_min < 0) x_min = 79;
            if (x_max > 79) x_max = 0;
            if (y_min < 0) y_min = 24;
            if (y_max > 24) y_max = 0;
            count_matrix[i][j] = matrix[y_max][x_max] + matrix[y_max][x_min] + matrix[y_min][x_max] +
                                 matrix[y_min][x_min] + matrix[i][x_max] + matrix[i][x_min] +
                                 matrix[y_max][j] + matrix[y_min][j];
        }
    }
}

void changing(int **matrix, int **count_matrix) {
    for (int i = 0; i < 25; ++i) {
        for (int j = 0; j < 80; ++j) {
            if (matrix[i][j] == 0 && count_matrix[i][j] == 3) {
                matrix[i][j] = 1;
            } else if (matrix[i][j] == 1 && (count_matrix[i][j] < 2 || count_matrix[i][j] > 3)) {
                matrix[i][j] = 0;
            }
        }
    }
}

void load_from_file(int **matrix, char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        printw("Error opening file %s\n", filename);
        refresh();
        return;
    }
    int x;
    for (int i = 0; i < 25; ++i) {
        for (int j = 0; j < 80; ++j) {
            fscanf(file, "%d", &x);
            matrix[i][j] = x;
        }
    }
    fclose(file);
}

void draw_ui_info(int speed) {
    printw("\nDelay: %d ms | Controls: [A] Faster  [Z] Slower  [SPACE] Exit", speed / 1000);
    refresh();
}

void handle_user_input(int *speed, int *running) {
    int key = getch();
    if (key == ERR) {
        return;
    }
    if (key == 'a' || key == 'A') {
        if (*speed > MIN_SPEED) {
            *speed -= SPEED_STEP;
        }
    } else if (key == 'z' || key == 'Z') {
        if (*speed < MAX_SPEED) {
            *speed += SPEED_STEP;
        }
    } else if (key == ' ') {
        *running = 0;
    }
}
