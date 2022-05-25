#include <iostream>
// Exercise from http://cppstudio.com/post/2591/
int main(){
    int number, n1, n2, n3, n4, n5;
    std::cout << "Enter a 5-symbol number: ";
    std::cin >> number;
    if (number >= 10000 && number <=99999){
        n1 = number % 10;
        n2 = number % 100 / 10;
        n3 = number % 1000 / 100;
        n4 = number % 10000 / 1000;
        n5 = number % 100000 / 10000;
        std::cout << "First is " << n5 << ", second is " << n4  << ", third is " << n3  << ", fourth is " << n2  << " and fifth is " << n1 << std::endl;
    }else{
        std::cout << "Yo wtf?" << std::endl;
    } 
    return 0;
}