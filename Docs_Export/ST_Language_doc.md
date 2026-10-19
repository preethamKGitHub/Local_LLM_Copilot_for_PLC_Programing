# Structured Text Language Reference

ST provides a number of code elements to help you modularize and structure your program.

## Configuration

A configuration is used to abstract the hardware from the software part of the application. It defines all the resources of an application and consists of tasks, used to describe the order of execution of programs, and global variables, which declare I/O specific dependencies.

e.g.
CONFIGURATION PLC_1

END_CONFIGURATION


### Global variables

Are declared inside the configuration. They may, but do not have to, address hardware

### Task configuration
A task is an element of program execution that is executed either periodically or in case of certain events. The ST Compiler currently supports periodic interval tasks with an INTERVAL and a PRIORITY:

To take effect, a task must be linked to a program with a program configuration.

### Program configuration
A program configuration defines the programs of a resource and assigns them to tasks. If no task is assigned, a default cyclic task with the lowest priority is generated automatically for the program.

A program can be parameterized by passing arguments to it in the program configuration. The rules for parameter passing apply.

e.g.
CONFIGURATION PLC_1
    TASK Main(Interval := T#1000ms, Priority := 1);
    PROGRAM P1 WITH Main : ExampleProgram(true, gInt1);
    PROGRAM P2 WITH Main : ExampleProgram(false, gInt2);

    VAR_GLOBAL
        gInt1 : INT;
        gInt2 : INT;
    END_VAR
END_CONFIGURATION

PROGRAM ExampleProgram
    VAR_INPUT
        in : BOOL;
    END_VAR
    VAR_OUTPUT
        out : INT;
    END_VAR
    ;
END_PROGRAM


## Program organization unit
A program organization unit (POU) can be used to modularize and structure a portion of the application. The POU has a defined interface with inputs and outputs and can be called and executed several times.

### Program declaration

A program declaration defines a program, the variables it uses and the code body executed.

    e.g.
    PROGRAM SampleProgram
        ;
    END_PROGRAM

    A program can declare the following sections:

            1. Static
            2. Input
            3. Inout
            4. Output
            5. Temp
            6. External

    A program defines a struct containing the variables from the VAR_INPUT, VAR_OUTPUT and VAR sections. Variables from these sections retain their state over multiple cycles. Each instance of a program preserves its own state.

    Global variables specified via VAR_EXTERNAL or VAR_IN_OUT can change their state within a single cycle when other programs write to them.

### Class declaration
    A class is the basic construct to support object-oriented programming in ST. It encapsulates a set of data (field) and behaviors (methods) that belong together as a logical unit. The fields and methods are members of the class. More detailed information about object-oriented programming can be found in OOP Overview.md

   
    e.g. 
    CLASS Motor

    END_CLASS

    Class can declare only Static section "VAR" inside it.

    A VAR...END_VAR construct, if required, specifying the names and types of the variables of the class. Each variable can have an access modifier such as PUBLIC, PRIVATE, INTERNAL, or PROTECTED. If omitted, the default is PROTECTED. Variables can only be declared in the VAR section. The VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT and VAR_TEMP sections are not allowed.

    Class constants are constant fields inside a class that are declared by adding the CONSTANT keyword to a VAR section in the class. The visibility of these constants can be controlled using access modifiers. If an access modifier is used, the syntax is: VAR CONSTANT ACCESS-MODIFIER


### Method declaration
    A method is a POU similar to a function, but it is only callable with an instance of the declaring class or function block.

        e.g.
        CLASS Motor
            METHOD PUBLIC Start
                ;
            END_METHOD

            METHOD PUBLIC Stop
                ;
            END_METHOD
        END_CLASS

        A method can declare the following sections:

            1. Input
            2. Inout
            3. Output
            4. Temp
            5. External

### Function declaration
        A function is a POU that does not store its state, i.e. inputs, internals and outputs/results. It may or may not additionally declare a return value.

        e.g.
        FUNCTION Abs : INT
            ;
        END_FUNCTION

        
        A function can declare the following sections:

            1. Input
            2. Inout
            3. Output
            4. Temp
            5. External


### Function block declaration
    A function block is a program organization unit (POU) that represents a well-defined portion of the program for the purposes of modularization and structuring. Its declaration is similar to that of a function but it is able to preserve its state over multiple cycles like a class. It is also similar to a class in that it can have multiple instances, each of which preserves its own state. Function blocks also support methods.

            A function block can declare the following sections:

        1. Static
        2. Input
        3. Inout
        4. Output
        5. Temp
        6. External

        Note that the use of the access modifier PRIVATE is not applicable for FUNCTION_BLOCK, except in a static-section.

### Declaring a namespace
        A new namespace is declared using the keywords NAMESPACE and END_NAMESPACE.

        A namespace can contain the following language elements:

            1. Namespace
            2. Function
            3. Function block
            4. Class
            5. Interface
            6. Type

## Variable sections

    Variable sections can be used to describe the interface of a program organization unit (POU) by declaring variables. The sections enable the caller to pass and retrieve values from the POU. In addition, internal states can be preserved throughout the complete cycle of the application.

### Global variables
    Global variables are symbols that are globally available over all program organization units.
    It is declared in configuration section.

    A direct access at input (I), output (Q) or memory (M) area of the PLC can be designated as a global variable using the keyword AT. After the letter indicating the area, use X (BIT), B (BYTE), W (WORD), D (DWORD) or L (LWORD) to indicate the width. If no letter for width is used, the width is recognized as one bit. See the following examples.

    Global constants are declared at configuration level, like every other global variable, by adding the CONSTANT keyword to the VAR_GLOBAL section.

    Like any other global variable, a global constant variable is not accessible in a POU unless it is re-declared in the VAR_EXTERNAL section of the POU again with the CONSTANTmodifier.

    e.g.
    CONFIGURATION PLC_1
            VAR_GLOBAL
                counter : INT;  //Global var with no direct access
                myBool1 AT %I0.3 : BOOL;
                myBool2 AT %MX1 : BOOL;  //Equivalent to %MX1.0, %M1.0, %M1

                mySInt AT %QB1 : SINT := SINT#-7;  //Direct access with initializer
                myULInt AT %IL5 : ULINT;

                myChar AT %MB0 : CHAR := 'F';
                myWChar AT %QW1 : WCHAR;

                myByte AT %QB8 : BYTE := BYTE#123;
                myDWord AT %MD5 : DWORD;
            END_VAR

            VAR_GLOBAL CONSTANT
                ProcessValue1 : REAL := REAL#123.4;
                ProcessValue2 : DWORD := DWORD#16#F00D;
            END_VAR
    END_CONFIGURATION

#### Retentive variables (RETAIN)
        A variable declared with the storage modifier RETAIN will keep its last written value after a warm start of the PLC. Note that a warm start of the PLC is just a power off/power on transition. This may be caused by using a physical switch or by a power loss.

        CONFIGURATION Default
            VAR_GLOBAL RETAIN
                ProcessValue1 : REAL := REAL#123.4;
                ProcessValue2 : DWORD := DWORD#16#F00D;
            END_VAR

            VAR_GLOBAL
                ProcessValueRef : REF_TO REAL := REF(ProcessValue1);
            END_VAR
        END_CONFIGURATION


### External section
    The external section can be used to reference globally declared variables. It provides a way to declare dependencies on global variables explicitly.

    VAR_EXTERNAL

    END_VAR

    This section can be declared by the following program organization units:

    Program
    Method
    Function
    Function block


    VAR_EXTERNAL CONSTANT will make global variable read only in the POU.

### Input section
    The input section may be declared to pass arguments, for further processing, from the caller to the called program organization units. iecst VAR_INPUT END_VAR.

    This section can be declared by the following program organization units:

        Program
        Method
        Function
        Function block

### Inout section
    The inout section can be declared to pass arguments, for further processing, from the caller to the called program organization units. It also provides a way to store a processing result, generated within the unit called, directly in a variable outside the unit called.


    This section can be declared by the following program organization units:

        Program
        Method
        Function
        Function block


### Output section
    The output section can be used to pass a result from inside the declaring program organization unit to its caller. It is possible to pass more than just the return value from callee to caller if necessary.

    This section can be declared by the following program organization units:

        Program
        Method
        Function
        Function block

    Differences between inout section and output section:

        A value change for a variable of the inout section inside the POU is written directly to the corresponding variable outside the POU. Only the final value for a variable of the output section after execution of the POU is written to the corresponding variable outside the POU.
        For function blocks, a variable of the output section is part of the data structure of the function block, so it is preserved across multiple cycles and can be accessed even from outside the function block. A variable of the inout section, in contrast, is just a pointer to the actual variable outside, so it is not preserved.

### Temp section
    The temp section can be used to store interim results during the execution of a program organization unit.

    Values stored inside variables declared in this section will be lost after the POU executes.

    This section can be declared by the following program organization units:

        Program
        Method
        Function
        Function block


### Static section
    The static section can be used to store values that need to be available over multiple cycles. The static does not imply that variables or values are shared by multiple instances. Every instance of a POU declaring this section accesses only its own memory. If no access modifier is specified, the default accessibility is PROTECTED in a Class and PRIVATE in a Function Block.

    This section can be declared by the following program organization units:

        Program
        Class
        Method
        Function
        Function Block

    No static variables are stored over multiple cycles in the scope of methods and functions, so the behavior of this section is equivalent to the temp section.

    Local constants are declared at POU level in a VAR section by adding the CONSTANT keyword.


## Types and Variables

    Structured text offers a huge a variety of different data types. A data type specifies how a given address in memory (named with a variable name) is to be interpreted, i.e. how many bytes are covered by a variable and how it is interpreted.

    Some of the data types are already predefined by the ST language, while others may be defined by the user on demand.

    The following paragraphs describe the supported data types.

### Elementary data types
    Elementary types are types already embedded in the language itself.

        Type	Literal example	Domain range	Size	Default
        BOOL	TRUE	0 ‥ 1	1 bit unsigned	FALSE
        BYTE	BYTE#2#1111_0101	0 ‥ 255	8 bit unsigned	BYTE#0
        WORD	WORD#32767, WORD#16#7FFF	0 ‥ 65535	16 bit unsigned	WORD#0
        DWORD	DWORD#16#ABCD_EF01	0 ‥ 4294967295	32 bit unsigned	DWORD#0
        LWORD	LWORD#55	0 ‥ 18446744073709551615	64 bit unsigned	LWROD#0
        SINT	SINT#-5	-128 ‥ 127	8 bit signed	SINT#0
        INT	-5	-32768 ‥ 32767	16 bit signed	0
        DINT	DINT#-56	–2147483648 ‥ 2147483647	32 bit signed	DINT#0
        LINT	LINT#512	-9223372036854775808 ‥ 9223372036854775807	64 bit signed	LINT#0
        USINT	USINT#5	0 ‥ 255	8 bit unsigned	USINT#0
        UINT	UINT#512	0 ‥ 65535	16 bit unsigned	UINT#0
        UDINT	UDINT#512	0 ‥ 4294967295	32 bit unsigned	UDINT#0
        ULINT	ULINT#512	0 ‥ 18446744073709551615	64 bit unsigned	ULINT#0
        REAL	REAL#5.0	-3.402823e+38 ‥ +3.402823e+38	32 bit (23 bit significant, 8 bit exponent)	REAL#0.0
        LREAL	3.14159	-1.79769313486231e+308 ‥ 1.79769313486231e+308	64 bit (52 bit significant, 11 bit exponent)	0.0
        TIME	TIME#12d2h4m8s16ms	–9223372036854ms ‥ 9223372036854ms	64 bit signed	TIME#0ms
        LTIME	LTIME#100000d2h4m8s16ms32ns	-9223372036854775808ns ‥ 9223372036854775807ns	64 bit signed	LTIME#0ns
        DATE	DATE#1980-01-23	1970-01-01 ‥ 2262-04-11	64 bit signed	DATE#1970-01-01
        LDATE	LDATE#1980-01-23	1970-01-01 ‥ 2262-04-11	64 bit signed	LDATE#1970-01-01
        TIME_OF_DAY	TOD#13:14:33.123	0:0:0.0 ‥ 23:59:59.999999999	64 bit signed	TOD#0:0:0.0
        LTIME_OF_DAY	LTOD#13:14:33.123456	0:0:0.0 ‥ 23:59:59.999999999	64 bit signed	LTOD#0:0:0.0
        DATE_AND_TIME	DT#1980-01-23-13:14:33.123	1970-01-01-0:0:0.0 ‥ 2262-04-11-23:47:16.854775807	64 bit signed	DT#1970-01-01-0:0:0.0
        LDATE_AND_TIME	LDT#1980-01-23-13:14:33.123456	1970-01-01-0:0:0.0 ‥ 2262-04-11-23:47:16.854775807	64 bit signed	LDT#1970-01-01-0:0:0.0
        CHAR	CHAR#'C'	0 ‥ 255	8 bit	CHAR#0
        WCHAR	WCHAR#"W"	0 ‥ 65535	16 bit	WCHAR#0
        STRING	STRING#'ABC'		1-254 characters	''
        WSTRING	WSTRING#"ABC"		1-16328 wide characters	""


        Not explicitly typed decimal literals are implicitly typed as INT, e.g., 42 is equivalent to INT#42.

        Not explicitly typed floating-point literals are implicitly typed as LREAL, e.g., 3.14 is equivalent to LREAL#3.14.

        Decimal literals can also be encoded as hexadecimal (16#), octal (8#) or binary (2#). Grouping with _ is supported.


### User-defined data types
    User-defined types make it possible to declare custom types not known to the type system. These types are declared in a TYPE section. This section can be declared in a Namespace so that the declared type is part of this namespace. If not contained within a namespace, the type section must be declared with a global scope.

        A "TYPE ... END_TYPE" may contain one or more of the following types:

            Structured type without relative addressing
            Structured type with relative addressing
            Enumeration
            Data type with named values
            Named array

        A type may declare the following access modifier

        Public
        Internal


### Array
    An array is a data structure consisting of a collection of elements (values or variables), each identified by at least one array index or key. An array is stored such that the position of each element can be computed from its index tuple by a mathematical formula. The simplest type of array is a linear array, also called a one-dimensional array.

    e.g. 
    ARRAY[0..9] of INT

    An array may contain the following types:

        Elementary data type
        Structured type
        Enumeration
        Data type with named values
        Class


    usage e.g.

    two_dim_array : ARRAY[0..2, 0..2] OF INT := [1, 2, 3, 4, 5, 6, 7, 8, 9];
    arr : ARRAY[1..100] OF INT := [50(2), 50(3)];
   

    A variable-length array can ONLY be declared in the following variable sections:

    input, output or in-out section of methods and functions
    in-out section of Function block

#### Named array
        An array can be declared as a named type such as structured types. The array declaration can then be referred to by type name instead of in an anonymous way.

        TYPE
            FibonacciSequence : ARRAY[0..10] OF INT := [0, 1, 1, 2, 3, 5, 8, 13, 21, 34];
        END_TYPE

        used as Sequence : FibonacciSequence;
        UseFibSequence := Sequence[Index];

#### Variable-length array
    An array with variable length can be declared using one or more *, each of which represents one dimension. For example:

    VAR_IN_OUT
        oneDimArray: ARRAY [*] OF INT;
        sixDimArray: ARRAY [*, *, *, *, *, *] OF REAL;
    END_VAR

    A variable-length array cannot be initialized in the variable sections, e.g. myVariableLengthArray: Array [*] OF INT := [1, 2, 3];

    A variable-length array as a whole cannot be used in an assignment statement in the code body, e.g. myFixedLengthArray := myVariableLengthArray;

    If the index used exceeds the bounds in runtime when accessing a variable-length array element, the error may cause the PLC to stop.

    A variable-length array parameter is always treated like an in-out parameter: (1) a function or method call has to provide arguments for all variable-length array parameters, independent of the variable section in which they are declared; (2) variable-length array parameters are always passed by reference (i.e. the parameter is an implicit reference to the array that is passed as an argument; no copy of the argument array is created at runtime).

    Together with the built-in functions of LOWER_BOUND and UPPER_BOUND, variable-length arrays are especially useful for implementing algorithms on arrays when the actual bounds of each dimension are unknown at compile time. The following example shows the calculation of the average value of all elements in a matrix A (2-dimensional array) and the generation of its transpose. Note that the return value of LOWER_BOUND or UPPER_BOUND has the type of DINT.

    e.g.

    matrix: ARRAY [*, *] of INT; // 2 dimention

    FOR i := LOWER_BOUND(matrix, 1) TO UPPER_BOUND(matrix, 1) DO        //1st-dimension bounds (line)
        FOR j := LOWER_BOUND(matrix, 2) TO UPPER_BOUND(matrix, 2) DO    //2nd-dimension bounds (column)
            sum := sum + matrix[i, j];
        END_FOR;
    END_FOR;

    elementCount := (UPPER_BOUND(matrix, 1) - LOWER_BOUND(matrix, 1) + 1)
                    * (UPPER_BOUND(matrix, 2) - LOWER_BOUND(matrix, 2) + 1);


    In contrast to a variable-length array, a reference to a variable-length array can be used in every section (except inout section) of every kind of POU (program, function, function block, class, method), as well as in the global section, just like the other reference types. It can refer to any array with the same element data type and the same dimension count in the global section and static section. It can be assigned with another reference to a variable-length array or a reference to a fixed-length array, except that a reference to a fixed-length array cannot be assigned with a reference to a variable-length array.

    e.g.


    In contrast to a variable-length array, a reference to a variable-length array can be used in every section (except inout section) of every kind of POU (program, function, function block, class, method), as well as in the global section, just like the other reference types. It can refer to any array with the same element data type and the same dimension count in the global section and static section. It can be assigned with another reference to a variable-length array or a reference to a fixed-length array, except that a reference to a fixed-length array cannot be assigned with a reference to a variable-length array.

    e.g.

    VAR
        arr1 : ARRAY[1..2, 1..3] OF INT := [1,2,3,4,5,6];
        ref_arr: REF_TO ARRAY[1..2, 1..3] OF INT := REF(arr1);
        ref_arr_star1: REF_TO ARRAY[*,*] OF INT := REF(arr1);  
        ref_arr_star2: REF_TO ARRAY[*,*] OF INT;
        res: INT;
    END_VAR

    ref_arr_star1 := ref_arr;       //allowed
    ref_arr_star2 := ref_arr_star1; //allowed
    ref_arr := ref_arr_star1;       //WRONG: not allowed

    res := ref_arr_star1^[2,3];       //Dereferenced in the same way as ref to fixed-length array

    

### String types
    A STRING or WSTRING is a data structure consisting of a collection of characters (CHAR or WCHAR respectively), a current length and a maximum capacity.

    Declaration of string variables
    Strings are declared using the STRING or WSTRING keyword followed by an optional maximum capacity in brackets. The valid range of the maximum capacity is 1-254 for STRING and 1-16328 for WSTRING. The effects of omitting the maximum capacity depend on the section in which the declaration is located:

    If a STRING or WSTRING without an explicit capacity is declared as a function or method parameter (i.e. if the declaration is located inside a VAR_INPUT, VAR_IN_OUT, or VAR_OUTPUT section of a function or method) or as an in-out (VAR_IN_OUT) parameter of a function block, the caller of the function, method, or function block may pass an argument STRING/WSTRING with an arbitrary capacity (thus, the function, method, or function block must not assume that the STRING/WSTRING has a specific, fixed capacity). Note too that such an argument STRING/WSTRING is always passed by reference (i.e. the parameter is an implicit reference to the STRING/WSTRING that is passed as an argument; no copy of the argument STRING/WSTRING is created at runtime).
    In all other cases (note that this also includes VAR_INPUT and VAR_OUTPUT parameters of function blocks), a STRING or WSTRING without an explicit capacity has an implicit default capacity of 254


### Structured type without relative addressing
    Structured types (STRUCT) offer the possibility to extend the type system with user-declared types that structure other data types to create coherent, reusable units. Structured types can be declared in parallel with program organization units.

   

    A STRUCT without relative addressing may contain the following types: - Elementary data type - Array - Structured type without relative addressing - Enumeration - Data type with named values - Named array - Class - Function block

    Recursive declarations of structured types are not supported and will lead to a compile time error.

    e.g.

    TYPE
        Motor : STRUCT
            isRunning : BOOL;
        END_STRUCT;
        Vehicle : STRUCT
            m : Motor;
            displacement : INT;
        END_STRUCT;
    END_TYPE

    Structured types are initialized by assigning an initializer to an element of the structured type. Elements that are not listed in the initializer will be initialized with the default initializer for the type.

    Types that can be initialized by a structure initializer are:

    STRUCT
    Class
    Function block

    VAR_TEMP
        myVehicle : Vehicle := ( m := ( isRunning := true ) , displacement := 9 ) ;
            // all members are initialized

        myOtherVehicle : Vehicle := ( displacement := -1 ) ;
            // partial initialization, the other members will retain their specific initialization
    END_VAR


### Structured type with relative addressing
    If a STRUCT is to be declared in the GLOBAL section with a direct address (input or output of the PLC), each of its members must have relative addressing. For members of Boolean type, the size specifier must be X (1 bit). In all other cases, the size specifier must be B (8 bits). When instantiating the STRUCT in the GLOBAL section, the direct address must also use the size specifier B (8 bits), as shown in the example below:

    e.g.

        CONFIGURATION CFG
            PROGRAM P1 : PRG;
            VAR_GLOBAL
                telegramInst AT %IB10 : Telegram101;
            END_VAR
        END_CONFIGURATION

        PROGRAM PRG
            VAR_EXTERNAL
                telegramInst: Telegram101;
            END_VAR
            ;
        END_PROGRAM

        TYPE
            //Byte size = 4 + (8 * 2 * 2)
            Telegram101 : STRUCT
                i AT %B0 : INT;
                arr AT %B4 : ARRAY [3..4, 3..4] OF Telegram102;
            END_STRUCT;

            //Byte size = 8
            Telegram102 : STRUCT
                j AT %B0 : INT;
                myDWord AT %B4 : DWORD; // A gap between members is allowed.
            END_STRUCT;
        END_TYPE

        A STRUCT with relative addressing may only contain the following types: - Elementary data type except for types of time, date and string - Structured type with relative addressing - Array of the types above

        The use of a named array as a member of a structured type with relative addressing is not supported. This is because structured types with relative addressing have a unique layout tailored for use in the input and output of a PLC. An array inside such a STRUCT would inherit the layout property and since a named array is a named type, it cannot have two different type layouts.

        As shown in the example above, a STRUCT with relative addressing can ONLY be instantiated in the GLOBAL section (with a direct address) and linked in the EXTERNAL section (without writing a direct address because it is already defined in the GLOBAL section).

### Enumeration
An enumeration is a data type defined by a set of named, constant values.


This will declare the type Colors and the three constant values RED, GREEN and BLUE. Because the type Colors is closed after declaration, the compiler will ensure that there is no value of type Colors whose runtime value is not one of RED, GREEN and BLUE.

e.g.
TYPE
    TrafficLightColors : (Red, Yellow, Green); // Default will be Red
    ErrorStates : (OK, Failed, Pending) := Pending; // Default will be Pending
END_TYPE

### Data type with named values
    Similar to the enumeration data type where the values of enumerated identifiers are not known is the enumerated data type with named values. The declaration specifies the data type and assigns the values of the named values.

    A data type with named values is a data type defined by a set of named, constant values of a certain type with a dedicated value. The data type of the named values must be an elementary data type.

    e.g.
    TYPE
        Colors : INT (
            RED := 12,
            GREEN := 14,
            BLUE := 23
        );
    END_TYPE

### Reference data types
    Reference data types are different to the data types described above in that they are interpreted as memory addresses. They also carry information about how the addressed memory location is to be interpreted (i.e. the data type of the addressed memory location). Reference-type variables do not carry a value. This is quite a powerful concept, as it makes it possible to access values of variables that are defined in different scopes. Values do not need to be copied, which enhances performance, for example for structured-type variables or instances of classes. On the other hand, incorrect use can lead to programming errors that are difficult to see.

    To avoid such difficulties, there are differences from certain other languages such as C:

    The address cannot be changed – address arithmetic is not possible.
    It is not possible to allocate a new bunch of memory, so no memory leaks can occur.
    To avoid so-called dangling references, only references to global variables and static variables are possible.
    The following rules must be observed when using references:

    Unset reference-type variables have the value NULL.
    To set a variable to another variable, see the reference operator.
    To retrieve the value referenced by the variable, use the dereference operator.

#### Named reference data types
    A reference type can be declared as a named type such as structured types. The declared type can then be used by type name.

    e.g. 
    TYPE
        FibonacciSequenceRef : REF_TO ARRAY[0..10] OF INT;
    END_TYPE

    FUNCTION UseFibSequence : INT
        VAR_INPUT
            Sequence : FibonacciSequenceRef;
            Index : INT;
        END_VAR
        UseFibSequence := Sequence^[Index];
    END_FUNCTION

    Example: Reference types and their use
        CONFIGURATION Plant
            TASK Main(Interval := T#100ms, Priority := 1);
            PROGRAM P WITH Main : Run;

            VAR_GLOBAL
                fb_instances : ARRAY[0..5] OF MyFB;
                active_instance : int;
            END_VAR
        END_CONFIGURATION

        PROGRAM Run
            VAR_EXTERNAL
                active_instance : INT;
            END_VAR
            VAR_TEMP
                activeInst : REF_TO MyFB; // will point to a memory location of type 'MyFB'
                someNumber : INT;
                err : bool;
            END_VAR
            // some code to determine the active instance and some number

            activeInst := GetTheFB_Inst(active_instance);
            IF activeInst <> NULL THEN
                // Dereference the returned value and call the function block instance.
                activeInst^(x := someNumber, error => err);
            ELSE
                err := true;
            END_IF;

            // do your error handling

        END_PROGRAM

        // Returns a reference to a specific fb instance
        FUNCTION GetTheFB_Inst : REF_TO MyFB
            VAR_INPUT
                idx : INT;
            END_VAR
            VAR_EXTERNAL
                fb_instances : ARRAY[0..5] OF MyFB;
            END_VAR

            IF idx >= 0 AND idx <= 5 THEN
                GetTheFB_Inst := REF(fb_instances[idx]); // Get a reference to the fb instance
            ELSE
                GetTheFB_Inst := NULL;
            END_IF;
        END_FUNCTION

        FUNCTION_BLOCK MyFB
            VAR_INPUT
                x : int;
            END_VAR
            VAR_OUTPUT
                error : bool := false;
            END_VAR
            // do some code
            ;
        END_FUNCTION_BLOCK


    Initialization of reference types
Reference types can be initialized during declaration using a REF() operator. This is also allowed recursively independent of their textual ordering.

        CONFIGURATION Default
            VAR_GLOBAL
                arr : ARRAY [0..2] OF REF_TO myStruct := [REF(struct1), REF(struct2)];

                struct1 : myStruct := (x := REF(a));
                struct2 : myStruct := (x := REF(b));

                a : INT := 1;
                b : INT := 2;

                r_i : REF_TO INT := REF(a);
            END_VAR
        END_CONFIGURATION

        TYPE
            myStruct : STRUCT
                x : REF_TO INT;
            END_STRUCT;
        END_TYPE

        FUNCTION Func : INT
            VAR_EXTERNAL
                struct1 : myStruct;
            END_VAR
            VAR_INPUT
                i : REF_TO myStruct := REF(struct1);
            END_VAR
            Func := i^.x^;
        END_FUNCTION

