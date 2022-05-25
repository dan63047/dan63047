#include <iostream>
// Exercise from http://cppstudio.com/post/2588/
int main(){
    std::cout << "My formula is x = (a + b — f / a) + f * a * a — (a + b)" << std::endl << "Write a, b and f values (in order): ";
    int a, b, f, x;
    std::cin >> a >> b >> f;
    x = (a + b - f / a) + f * a * a - (a + b);
    std::cout << "x is " << x << std::endl;
}