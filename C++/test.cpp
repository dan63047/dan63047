#include <iostream>
// Exercise from http://cppstudio.com/post/1375/
int main(){
    int x;
    std::cout << "Enter array length" << std::endl;
    std::cin >> x;
    float *a = new float[x];
    for (unsigned i = 0; i < x; i++){
        a[i] = rand() % 100 / (rand() % 10 + 3.0);
        std::cout << std::fixed << a[i] << "  ";
    }
    std::cout << std::endl;
    float sum;
    for (unsigned i = 0; i < x; i++)
    sum += a[i];
    std::cout << "Average: " << (sum / x) << std::endl;
    delete [] a;
    return 0;
}