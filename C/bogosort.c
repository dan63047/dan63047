#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h> 
#include <time.h>
#include <locale.h>
#define NELEMS(x)  (sizeof(x) / sizeof(x[0]))
#define print_type(count, stmt) \
    do { \
    printf("["); \
    for (size_t i = 0; i < (count); ++i) { \
        stmt; \
    } \
    printf("\b]\n"); \
    } while (0)

void shuffle(unsigned long int *array, size_t n)
{
    if (n > 1) 
    {
        size_t i;
        for (i = 0; i < n - 1; i++) 
        {
          size_t j = i + rand() / (RAND_MAX / (n - i) + 1);
          int t = array[j];
          array[j] = array[i];
          array[i] = t;
        }
    }
}


char * num4(unsigned long num){
    char *res = malloc(6 * sizeof(char));
    sprintf(res, "%lu", num);
    const size_t length = NELEMS(res);
    if (length <= 4) {
        printf("here\n");
        return res;
    }
    printf("anti here\n");
    return res;
}

int correct(unsigned long  *arr, int size) {
    while ( --size > 0 )
        if (arr[size]-1 != arr[size-1])
            return 0;
    return 1;
}

int main(){
    unsigned long int arr_len;
    printf("Enter array length: ");
    scanf("%d", &arr_len);
    unsigned long int array[arr_len];
    unsigned long int i, steps, a, b, c;
    for (i = 0; i < arr_len; i++){
        array[i] = i;
    }
    shuffle(array, arr_len);
    printf("Array created: ");
    if (arr_len > 100){
        printf("%d values\n", arr_len);
    }else{
        print_type(NELEMS(array), printf("%d,", array[i]));
    }
    time_t start, end;
    time(&start);
    while(!correct(array, arr_len)){
        a = rand() % arr_len;
        b = rand() % arr_len;
        c = array[a];
        array[a] = array[b];
        array[b] = c;
        steps++;
        //printf("%d\r", steps);
    }
    time(&end);
    double wasted = difftime(end, start);
    struct timespec lol;
    timespec_get(&lol, NULL);
    printf("\nDone: ");
    if (arr_len > 100){
        printf("%d values sorted\n", arr_len);
    }else{
        print_type(NELEMS(array), printf("%d,", array[i]));
    }
    setlocale(LC_ALL, "en_US.UTF-8");
    printf("Steps: %'d\nWasted %'.0f seconds\nSpeed: %'f steps/second\n", steps, wasted, steps/wasted);
    printf(num4(steps));
    return 0;
}