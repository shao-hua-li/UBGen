




#include<stdint.h>

int foo(int p) 

{
    




uint32_t a[3]={0}, b=1;
    

uint32_t UNINIT_var;//UBFUZZ 
b=1;
    
{
        


int *c;
    }


    


if(/*initS*/b/*initE*/+UNINIT_var)
        

{


return 1;
}


    

return a[1];
}



int main() {
    
int x;
    x = foo(2);
}
