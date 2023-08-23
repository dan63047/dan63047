#include <iostream>
#include <cstring>
#include <locale>

void shuffle(long unsigned int *arr, int size) {
    for (int i = 0; i < size; ++i)
        std::swap(arr[i], arr[(rand() % size)]); 
}

bool correct(long unsigned int *arr, int size) {
    while (--size > 0)
        if (arr[size - 1] > arr[size])
            return true;
    return false;
}

std::string num4(unsigned long int num){
    std::string cnum = std::to_string(num);
    if (cnum.length() <= 4) {
        printf("here\n");
        return cnum;
    }
    std::string postfixs = "kMBTqQsS";
    int nl = cnum.length()-1;
    int scale = std::min(int(nl / 3), 8);
    num /= 10^(3*scale);
    int decimal_length;
    if(int(nl / 3) <= 8){
        decimal_length = 2 - nl % 3;
    }else{
        decimal_length = 0;
    }
    cnum = std::to_string(num) + postfixs[scale-1]; //f"{num:.{decimal_length}f}{postfixs[scale-1]}";
    return cnum;
}
int main(){
    unsigned long int array_length, i, steps, a, b, c, wasted;
    time_t start, end;
    std::cout << "Enter array length: " << std::endl;
    std::cin >> array_length;
    unsigned long int array[array_length];
    for (i = 0; i < array_length; i++){
        array[i] = i;
    }
    shuffle(array, array_length);
    if (array_length > 100){
        std::cout << "Array created: " << array_length << " values in the array\n";
    }else{
        std::cout << "Array created: " << array << " \n";
    }
    time(&start);
    steps = 0;
    while(correct(array, array_length)){
        a = rand() % array_length;
        b = rand() % array_length;
        c = array[a];
        array[a] = array[b];
        array[b] = c;
        steps++;
        //printf("%d\r", steps);
    }
    time(&end);
    wasted = difftime(end, start);
    if (array_length > 100){
        std::cout << "Done: " << array_length << " values\n";
    }else{
        std::cout << "Done: " << array<< " values\n";
    }
    double steps_on_sec;
    if (wasted > 0){
        steps_on_sec = steps/wasted;
    }else{
        steps_on_sec = 0;
    }
    setlocale(LC_ALL, "en_US.UTF-8");
    printf("Steps: %'d\nWasted %'d seconds\nSpeed: %'f steps/second\n", steps, wasted, steps_on_sec);
    std::cout << num4(steps) << std::endl;
    return 0;
}