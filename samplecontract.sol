pragma solidity ^0.4.22;

contract VariableTest
{
    bool[] public bools;
    bool public v1 = true;
    bool public v2 = false;
    bool public v3 = true;
    bool public v4 = true;
    bool public v5 = true;
    int16[2] public int16array;
    bool public v6 = true;
    bool public v7 = true;

    mapping(int16 => int16)[2][4] public balances2;
    int x;
    int8 public v10 = 49;
    int[] arr2;
    bool public v11 = true;
    bool public v12 = false;
    bool public v13 = true;
    byte[] arr3;
    int public v8 = 10;
    bool public v9 = true;
    int16[] arr1;
    struct TestStruct
    {
        int16[4][5] v1;
        int16 v2;
    }
     int y;
    mapping(int16 => int16)[][] public balances;
    int z;

    struct TestStruct2
    {
        int[] v1;
        int[] v2;
    }

    int16 public v14 = 55;
    int120 public v15 = 21012;
    bool[50] public longenough;
    uint32 public v16 = 743;
    int184 public v17 = 5999995;
    TestStruct  mystruct;
    uint72 public v18 = 2101112;
    int240 public v19 = 74111183;
    bool[5] public boolarray;
    int8[5] public int8array;
    int16 public test;

    int16 hi = 9999;


    int16 bye = 1111;
    string[5] string5;
    bytes[5] byte5;
    string[35] strings35;
    bytes[35] byte35;

    string[5][1] string51;
    string[][] stringdd;

    address public hello = 0xEf5c7EEB790338422858F44Aed3b590a79e9b7bF;
    bool[10] public boolarray2;
    bool public emptybool;
    // TestStruct2 anotherstruct;
    address public another = 0x133954422C3b3E2E99Afd056dA832f4bee347DB8;
    int8 public newint=0x59;
    enum FreshJuiceSize{ SMALL, MEDIUM, LARGE }
    FreshJuiceSize[][] choice;

    enum BigEnum{A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, AA, BB, CC, DD, EE, FF, GG, HH, II, JJ}
    BigEnum choice2;

    int248 public empty;

    int104[3][5][4] public hellllo;

    bool[][] public array1;
     bool [][5] hel; //5 times dynamic
    bool [5][] hellop;
    int [5][2] h;
    int104[][] public array6;
    // mapping(int=>int) map;

    constructor() public
    {



        choice.push([FreshJuiceSize.LARGE, FreshJuiceSize.LARGE, FreshJuiceSize.SMALL, FreshJuiceSize.SMALL]);
        choice.push([FreshJuiceSize.MEDIUM, FreshJuiceSize.MEDIUM, FreshJuiceSize.LARGE, FreshJuiceSize.MEDIUM, FreshJuiceSize.MEDIUM]);
        choice2 = BigEnum.BB;
        boolarray2[5] = true;
        test = 9999;
        emptybool = true;
        for (int i =0; i<35; i++)
        {
            bools.push(true);
        }
        hel[0] = [true, false, true, false, true, false, true, true, true, true];
         hellop.push([false, true, true, true, true]);

         hellop.push([false, true, true, true, true]);
         hellop.push([false, true, true, true, true]);
        arr3.push('a');
        arr1.push(22);
        arr1.push(99);
        array1.push([true, true, false, false, true, false, true]);

        array1.push([true, true, true]);

        array1.push([true]);

        string5[0] = "This is string 1";
        string5[1] = "this is string 2";
        string5[2] = "this is string 3, which is really long so it cant be put at a fixed index";
        string5[3] = "ok so how this works?";


        byte5[0] = "This is string 1";
        byte5[1] = "this is string 2";
        byte5[2] = "this is string 3, which is really long so it cant be put at a fixed index";
        byte5[3] = "ok so how this works?";
         x = 234249945661;
          y = 234324444444;
        string51[0][4] = "ok lets see what happens";
        stringdd.push(["ok so this is A", "this is B", "this is another string whch is a dynamic i.e. it is C hash"]);

          z = 11111119999111;
        stringdd.push(["hello, i am a not so long string ok"]);

        stringdd.push(["hello, i am a loooooooooooooooooooooooooong string ok"]);

        array6.push([987123987, 972937, 129739]);

        array6.push([892173, 987213, 819237, 82173, 12736, 872136]);
        hellllo[3][4][2] = 213123;
        hellllo[1][2][1] = 23432;
        hellllo[2][1][2] = 4443;
        hellllo[0][2][2] = 213232;
        hellllo[2][3][2] = 9998;

        v1=true;
        v2=false;
        arr3.push('x');
        v3=true;
        v4=true;
        v5=true;
        v6=true;
        arr2.push(999898999);
        v7=false;
        v10 = 49;//int8
        v8 = 10; //int256
        v9=true;
    }
}

