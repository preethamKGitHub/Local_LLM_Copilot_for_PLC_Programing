# Expressions

An expression, in contrast to a statement, is evaluated to a value and combined with other expressions for complex computations. An expression cannot be used as a statement on its own and must always be part of a larger statement. This does not apply in the case of calls, which can be used as a statement and as an expression.

Literals
Literals are the simplest form of expression. They represent a single unchangeable value. Different forms are written in different ways.

BOOL literals
For BOOL literals, the keywords FALSE and TRUE are used. BOOL#0 and BOOL#FALSE or BOOL#1 and BOOL#TRUE are in each case equivalent.

Number literals
Number literals represent numbers such as 0, 1, 2, 3, …. There are various formats for writing them.

Form of literal	Format	Example(s)
Decimal untyped	[+-]?[0-9]+	-1, +255
Hexadecimal untyped	16#[0-9A-F]+	16#1, 16#FF
Octal untyped	8#[0-7]+	8#1, 8#377
Binary untyped	2#[0-1]+	2#1, 2#11111111
Decimal typed	TYPE + #[+-]?[0-9]+	WORD#65535, BYTE#255
Hexadecimal typed	TYPE + #16#[0-9A-F]+	UINT#16#FFFF, BYTE#16#FF
Octal typed	TYPE + #8#[0-7]+	INT#8#1, USINT#8#377,
Binary typed	TYPE + #2#[0-1]+	SINT#2#1, USINT#2#11111111
REAL/LREAL typed	TYPE + #[+-]?[0-9]+\.[0-9]+([Ee][+-]?[0-9]+)?	REAL#-1.2E+34, LREAL#12.34
 
String and character literals
Character literals may be written like typed number literals. They may also be written like typed or untyped string literals of length one.

Form of literal	Format	Example(s)
Decimal typed	TYPE + #[+-]?[0-9]+	CHAR#255, WCHAR#65535
Hexadecimal typed	TYPE + #16#[0-9A-F]+	CHAR#16#FF, WCHAR#16#FFFF,
Octal typed	TYPE + #8#[0-7]+	CHAR#8#377, WCHAR#8#177777,
Binary typed	TYPE + #2#[0-1]+	CHAR#2#11111111, WCHAR#2#123,
1-String untyped	…	'A', "B", "$0001" , '$01', '$$'
1-String typed	…	WCHAR#'A', CHAR#'A', WCHAR#"B",
 
String literals are either typed or untyped and are delimited by single quotes ' for CHAR content and by double quotes " for WCHAR content. Control characters cannot be included but can be represented by escape sequences initiated with $.

Form of literal	Format	Example(s)
Single quote untyped	'.*'	'abc', '123'
Single quote typed	_TYPE_#'.*'	STRING#'123', WSTRING#'123'
Double quote untyped	".*"	"abc", "123"
Double quote typed	_TYPE_#".*"	WSTRING#"123", WSTRING#"123"
 
String escape sequences
Escape sequences in strings are initiated with a dollar sign $ followed by various types of sequence:

Escape sequence	Format	Example(s)
Escape for dollar sign	$$	'This will cost you $$2.', CHAR#'$$'
Escape for line feed	$[Ll]	"$L", "$l"
Escape for carriage return	$[Rr]	'$R', "$r"
Escape for new line (CR+LF)	$[Nn]	'one line$Nanother line', "$N"
Escape for horizontal tab	$[Tt]	'$T', "Some $t formatting"
Escape for page feed	$[Pp]	'$p', "$P"
Escape for single quote	$'	STRING#'He said $'oh$'.'
Escape for double quote	$"	WSTRING#"She said $"no$"."
Escape for CHAR-Hex-Code	$[0-9A-F]{2}	'She$20jumped$20spaces'
Escape for WCHAR-Hex-Code	$[0-9A-F]{4}	"He$0020jumped$0020spaces"
 
Date and time literals
The following table uses the following placeholders for

the year: \Y = [0-9]{4}, for example 1998
the month and day: \M, \D = [0-9]{1,2}, for example 2, 05, or 11
the hours, minutes, and seconds: \h, \m, \s = [0-9]{1,2}, for example 3, 04, or 22
the milliseconds: \3 = [0-9]{1,3}, for example 1, 02, or 003
the nanoseconds: \9 = [0-9]{1,9}, for example 1, 0002, or 123456789
a decimal number with fractional part: \N = [0-9]+(\.[0-9]+)?, for example 3, 0.4, or 123.456
Data types	Format	Possible prefixes	Smallest unit	Example(s)
DATE, LDATE	PREFIX + #\Y-\M-\D	DATE, LDATE, D, LD	Day	DATE#2007-01-09, D#2007-01-09, LDATE#2007-06-29, LD#2007-06-29
TIME	PREFIX + #[+-]?(\Nd)?(\Nh)?(\Nm)?(\Ns)?(\Nms)?
There must be at least one component. Only the last component may have a fractional part. The fraction must result in an integer number of milliseconds.	TIME, T	Millisecond	TIME#1h30m500ms, T#2.2s=T#2s200ms
⚠ rejected: T#0.000001h (would be 3.6ms)
LTIME	PREFIX + #[+-]?(\Nd)?(\Nh)?(\Nm)?(\Ns)?(\Nms)?(\Nus)?(\Nns)?
There must be at least one component. Only the last one may have a fractional part. The fraction must result in an integer number of nanoseconds.	LTIME, LT	Nanosecond	LTIME#5ms2us, LT#+5ms2us1ns, LTIME#1.12345678s
TIME_OF_DAY	PREFIX + #\h:\m:\s(\.\3)?	TIME_OF_DAY, TOD	Millisecond	TIME_OF_DAY#13:10:02, TOD#13:10:02.001, TOD#2:3:4
LTIME_OF_DAY	PREFIX + #\h:\m:\s(\.\9)?	LTIME_OF_DAY, LTOD	Nanosecond	LTIME_OF_DAY#13:10:02.001002003, LTOD#13:10:02.001002003, LTOD#1:2:3
DATE_AND_TIME, LDATE_AND_TIME	PREFIX + #\Y-\M-\D-\h:\m:\s(\.\9)?	DATE_AND_TIME, LDATE_AND_TIME, DT, LDT	Nanosecond	DATE_AND_TIME#2007-01-09-09:43:00, DT#2007-01-09-09:43:00.0, LDATE_AND_TIME#2007-01-09-09:43:00.123456789, LDT#2007-01-09-09:43:00.123456789, DT#1970-1-1-1:1:1
 
Note

Literals may not exceed the range of their respective type.
DATE, LDATE, DATE_AND_TIME, and LDATE_AND_TIME literals must represent valid dates.
TIME_OF_DAY, LTIME_OF_DAY, DATE_AND_TIME, and LDATE_AND_TIME literals must represent valid times of day and exclude leap seconds.
Operators
The following table lists all available operators. For some operators, the data types do not have to be equal and the result data type might be different to the operands' data type, see restrictions in the table below.

Operation	Syntax Example	Restrictions
Constant evaluation	1234, Colors#Red	
Variable evaluation	X	
Reference	REF(X)	The type of X must be a non-reference type. A reference to a character of a STRING / WSTRING or partial access is not allowed.
Name of a function, variable, type or member as string constant	NAME_OF(X)	NAME_OF is evaluated at compile time and has no effect at runtime
Rotate left	ROL(X, Y)	X must be of bit-aware data type, Y must be an unsigned integer type
Rotate right	ROR(X, Y)	X must be of bit-aware data type, Y must be an unsigned integer type
Shift left	SHL(X, Y)	X must be of bit-aware data type, Y must be an unsigned integer type
Shift right	SHR(X, Y)	X must be of bit-aware data type, Y must be an unsigned integer type
Conversion	TO_<TYPE>(X)	Explicitly converts X in the datatype <TYPE> acc. to table in IEC61131-3
Array bounds	LOWER_BOUND(array, 6), UPPER_BOUND(array, 2)	Returns lower/upper bound of a given dimension of the variable-length array
Sub-expression evaluation	(A + B)	
Member access	instance.member	
Partial access	X.%W1	See detailed explanation below
Invocation	F(Z := A)	
Array access	array[index]	index must be of integer data type (for example INT). Access may lead to an out-of-bounds error.
Indexed string access	myString[index]	index must be of integer data type (for example INT) and greater than 0 (acc. to IEC61131-1, access to a STRING is 1-based). Access may lead to an out-of-bounds error. In addition, passing myString[index] to a VAR_IN_OUT is not allowed.
Dereference	X^	The type of X must be a reference type (REF_TO <some_type>)
Unary plus	+X	Operands of ANY_SIGNED, ANY_DURATION and ANY_REAL data types (e.g. INT, LTIME or REAL) are applicable.
Negation	-X	Operands of ANY_SIGNED, ANY_DURATION and ANY_REAL data types (e.g. INT, LTIME or REAL) are applicable.
Complement	NOT X	The operand must be of type BOOL
Exponentiation	X ** Y	The base must be any REAL, the exponent can be any REAL or ANY_NUM data type (e.g. INT). Mixing real data types between base and exponent is not possible (e.g. REAL ** LREAL).
Multiplication	X * Y	Operands of ANY_NUM data types (e.g. INT or REAL) are commutative and must be of equal type, operands of ANY_TIME data types must be given first followed by an ANY_NUM, see Arithmetic on date and time types.
Division	X / Y	Operands of ANY_NUM data types must be equal, operands of ANY_TIME data types must be given first followed by an ANY_NUM, see Arithmetic on date and time types.
Remainder	X MOD Y	Operands must be of integer data type (e.g. INT)
Addition	X + Y	Result date type is ANY_DATE for ANY_DATE - ANY_DURATION, otherwise the result data type is ANY_MAGNITUDE. Operator is invalid for other data types. See Arithmetic on date and time types.
Subtraction	X - Y	Result date type is ANY_DATE for ANY_DATE - ANY_DURATION, for ANY_DATE - ANY_DATE the result data type is ANY_TIME, otherwise the result data type is ANY_MAGNITUDE. Operator is invalid for other data types. See Arithmetic on date and time types.
Equality	X = Y	
Less than	X < Y	Operands must have an order
Greater than	X > Y	Operands must have an order
Inequality	X <> Y	
Less than or equal to	X <= Y	Operands must have an order
Greater than or equal to	X >= Y	Operands must have an order
Conjunction (eager operator)	X AND Y or X & Y	Operands must be of bit-aware data types: BOOL, BYTE, WORD, DWORD, LWORD
Exclusive disjunction	X XOR Y	Operands must be of bit-aware data types: BOOL, BYTE, WORD, DWORD, LWORD
Disjunction (eager operator)	X OR Y or X \| Y	Operands must be of bit-aware data types: BOOL, BYTE, WORD, DWORD, LWORD
Conjunction (short-circuit operator)	X && Y	Operands must be of BOOL type
Disjunction (short-circuit operator)	X \|\| Y	Operands must be of BOOL type
 
Arithmetic on date and time types
The compiler supports arithmetic operations only for specific combinations of date/time types.

Addition and subtraction
Operations	Result type	Note
TIME + TIME	TIME	
TIME - TIME	TIME	
LTIME + ANY_DURATION	LTIME	
ANY_DURATION + LTIME	LTIME	
LTIME - ANY_DURATION	LTIME	
ANY_DURATION - LTIME	LTIME	
TOD + TIME	TOD	
TOD - TIME	TOD	
LTOD + LTIME	LTOD	
LTOD - LTIME	LTOD	
DT + TIME	DT	
DT - TIME	DT	
LDT + LTIME	LDT	
LDT - LTIME	LDT	
DATE - DATE	TIME	Equivalent to LDATE - LDATE with a conversion of the result to TIME.
LDATE - LDATE	LTIME	
TOD - TOD	TIME	
LTOD - LTOD	LTIME	
DT - DT	TIME	Equivalent to LDT - LDT with a conversion of the result to TIME.
LDT - LDT	LTIME	
 
Note

For non-duration types, mixed short/long date-time arithmetic is not allowed (for example DT - LDT or TOD + LTIME). Instead, explicitly convert one of the operands to the type of the other one.
DATE and LDATE do not support addition or subtraction with durations. Instead, you can cast to DATE_AND_TIME or LDATE_AND_TIME beforehand.
DATE - DATE and DT - DT only support a difference of up to the range of TIME (T#-24d_20h_31m_23s_648ms to T#24d_20h_31m_23s_647ms). For larger differences, use LDATE - LDATE or LDT - LDT instead.
Multiplication and Division
Operations	Result type
TIME * ANY_NUM	TIME
LTIME * ANY_NUM	LTIME
TIME / ANY_NUM	TIME
LTIME / ANY_NUM	LTIME
 
ANY_NUM can be any number type (SINT to LINT, USINT to ULINT, REAL and LREAL).

Note

For REAL or LREAL, the multiplication or division operation is performed at LREAL precision and the result converted to the type of the left-hand operand (TIME or LTIME). This may lead to inaccurate results because LREAL cannot represent large LTIME values accurately. For example, LTIME#104d5h59m59s254740993ns * LREAL#1.0 results in LTIME#104d5h59m59s254740992ns.

Evaluation of operations
Operations with higher precedence are evaluated before operations with lower precedence. Operations of equal precedence and operations with two operands are evaluated from left to right (left associative), so the expression a + b - c, for example, is evaluated as (a + b) - c.

The exact precedences of operators are listed below from highest to lowest. Alternative operators in the diagram, such as *, / and MOD, have equal precedence.

expression:

Potential perfomance impact for operations including calls

To ensure the correct evaluation order the ST Compiler can insert shadow copies, which can impact performance. In the case of binary expressions only the left-most expression may need to be copied, so in the case of e.g. x := a + foo() the ST Compiler may generate a shadow copy of a, because foo might mutate it, through possible side effects. If the operation is commutative the shadow copy can be avoided by reordering the expression to x := foo() + a. In this case foo is evaluated first and side effects on a are considered intentional. In the case of array accesses these shadow copies can happen for two reasons: 1. The array instance expression dereferences a REF_TO variable, if an index is a call. For example x := arrRef^[foo()] causes a shadow copy of the address arrRef points to, but

    i := foo();
    x := arrRef^(i);
does not, because foo() could change which ARRAY arrRef references. 2. The indices contain a call, which causes all preceding indices to generate a shadow copy. For example in arr[x, foo(), y], x is copied, because foo could mutate it, but since we evaluate from left to right y does not need to be copied, because the call to foo happens before we evaluate y and side effects on y are considered intentional.
Eager operators and short-circuit operators
As shown in the table above, there are different kinds of Boolean logical operators for conjunction and disjunction:

Eager operators (&, AND, |, OR) always evaluate the left operand first and then the right operand.

Short-circuit operators (&&, ||) only evaluate the right operand if necessary, i.e. the right operand will not be evaluated when the left operand of && is false, or when the left operand of || is true.

The difference between eager and short-circuit operators can lead to different side effects of evaluation, as shown in the example below.

CONFIGURATION PLC_1
    PROGRAM P1 : SampleProgram;
    VAR_GLOBAL
        sideEffect, sideEffectAmp, sideEffectDoubleAmp, sideEffectPipe, sideEffectDoublePipe, sideEffectComplex: INT;
    END_VAR
END_CONFIGURATION

PROGRAM SampleProgram
    VAR_EXTERNAL
        sideEffect, sideEffectAmp, sideEffectDoubleAmp, sideEffectPipe, sideEffectDoublePipe, sideEffectComplex: INT;
    END_VAR
    VAR
        b: BOOL;
    END_VAR
    b := F(1) & T(2);                       // Evaluate left operand and then right operand
    sideEffectAmp := sideEffect;            // 2

    b := F(1) && T(2);                      // Evaluate only left operand
    sideEffectDoubleAmp := sideEffect;      // 1

    b := T(1) | F(2);                       // Evaluate left operand and then right operand
    sideEffectPipe := sideEffect;           // 2

    b := T(1) || F(2);                      // Evaluate only left operand
    sideEffectDoublePipe := sideEffect;     // 1

    b := T(1) | F(2) || T(3) && T(4) & F(5);
    // Equivalent to ( T(1) | F(2) ) || ( T(3) && ( T(4) & F(5) ) )
    // Evaluate left operand of "||" : T(1) | F(2)
    // Evaluate T(1) and then F(2)
    // T(1) | F(2) is true, no need to evaluate right operand of "||"
    sideEffectComplex := sideEffect;        // 2
END_PROGRAM

FUNCTION F: BOOL
    VAR_EXTERNAL
        sideEffect: int;
    END_VAR
    VAR_INPUT
        i:int;
    END_VAR
    sideEffect := i;
    F := FALSE;
END_FUNCTION

FUNCTION T: BOOL
    VAR_EXTERNAL
        sideEffect: int;
    END_VAR
    VAR_INPUT
        i:int;
    END_VAR
    sideEffect := i;
    T := TRUE;
END_FUNCTION
Partial variable access
Variables of all numeric and bit data types (except BOOL) support access to parts of their values. A partial access needs to specify an access width and an offset, similarly to directly represented variables. The offset depends on the access width, is zero-based and starts from the least significant bit.

The following table shows how the offset is interpreted when accessing a DWORD variable:

Partial access width

Examples:

FUNCTION MyFunction
    VAR_TEMP
        MyBool: BOOL;
        MyByte: BYTE;
        MyWord: WORD;
        MyDWord: DWORD;
        MyLWord: LWORD;
    END_VAR
    MyBool := MyByte.%X0; // Read the first bit of MyByte
    MyWord.%B1 := MyByte; // Write MyByte to second byte of MyWord
    MyBool := MyDWord.%X15; // Read the 16th bit of MyDWord
    MyLWord.%W1 := MyWord; // Write MyWord to the second word of MyLWord
    MyWord := MyLWord.%W1; // Read the second word of MyLWord
    MyByte := MyLWord.%B1; // Read the second byte of MyLWord

END_FUNCTION
Note

Varying the IEC standard, it is mandatory to specify the access width explicitly.

Calls
Invocations are used to call functions or methods. ST offers two different kinds of calls, namely formal calls (for which the names of the formal parameters have to be stated explicitly) and informal calls (for which the names of the formal parameters do not have to be stated explicitly):

CallExpression:
expression
'('
parameterList
')'
parameterList:
','
expression
':='
'=>'
expression

During runtime, the arguments provided in a function call or method call are passed to the function or method called (the so-called "callee"). How this works depends on the section in which the formal parameters of the callee are declared and on their types, see below for details. ST also supports co-variant type conversions for VAR_INPUT parameters, see below for details.

Note too that ST supports the overloading of functions and methods (i.e. the declaration of multiple functions or methods with the same name, but different signatures). Details can be found in the dedicated section on overloading.

Formal calls
This is the formal way to perform an invocation. During the call, the formal parameters are mentioned explicitly when assigning an argument to it. The assignment operators := and => are used to assign an argument according to the declaration of the function's variables. Only variables of the section VAR_INPUT, VAR_OUTPUT and VAR_IN_OUT are treated as call parameters and can be assigned in a call. Because the formal parameter name is explicitly given, the order of arguments in the call is arbitrary.

When performing a formal call, all parameters, except for VAR_IN_OUT, can be omitted. If a parameter is omitted, the optional initial value or default value of the variable will be used as the argument. VAR_OUTPUT parameters are always initialized with the initial value (if explicitly specified) or the parameter type's default value.

Formal calls make it possible to pass augments in an order other than the order in which the parameters are declared at the callee. This is possible because every parameter is explicitly named and no ambiguity exists. However, the order in which arguments are evaluated is still determined by the formal declaration of the callee.

Example: Formal calls
PROGRAM Invocation
    VAR_TEMP
        a : INT := 10;
        b : INT;
    END_VAR

    a := Func(in := 1, inout := a, out => b); // arguments: in = 1, out = b.
    a := Func(inout := a, out => b, in := 1); // order does not matter
    a := Func(inout := a); // arguments: in = 100, out = 110.
END_PROGRAM

FUNCTION Func : INT
    VAR_INPUT
        in : INT := 100;
    END_VAR
    VAR_OUTPUT
        out : INT := 110;
    END_VAR
    VAR_IN_OUT
        inout : INT;
    END_VAR

    out:= in * out;
    Func := out + inout;
END_FUNCTION
Informal calls
Unlike formal calls, informal calls do not need the formal parameter name to be mentioned explicitly. You may pass the arguments directly in the call observing the order in which they are declared in the called function or method. Informal calls are subject to the same parameter passing rules as formal calls.

When performing an informal call, parameters to the right of the parameter list can be left out, except for VAR_IN_OUT. If a parameter is omitted, the optional initial value or default value of the variable will be used as the argument. VAR_OUTPUT parameters are always initialized with the initial value (if explicitly specified) or the parameter type's default value. Note that arguments are strictly bound from left to right in the formal parameter list, so only parameters to the right of a parameter list may be omitted.

Note

You may not combine informal and formal call styles in the same call.

Example: Informal call
FUNCTION Callee : INT
    VAR_INPUT
        in : INT;
    END_VAR
    VAR_TEMP
        temp : INT;
    END_VAR
    VAR_OUTPUT
        out : INT;
    END_VAR
    VAR_IN_OUT
        inout : INT;
    END_VAR

    Callee := 0;
END_FUNCTION

PROGRAM Invocation
    VAR_TEMP
        a,b : INT;
    END_VAR

    a := 10;
    a := Callee(1, a, b); //same as Callee(in := 1, inout := a, out => b);
    a := Callee(1, a);    //same as Callee(in := 1, inout := a, out => 0);
END_PROGRAM
Parameter passing
How an argument is passed to the callee depends on the section in which the corresponding formal parameter is declared and on the formal parameter's declared type:

VAR_IN_OUT parameters are always passed by reference. The formal parameter is only an (implicit) reference to the argument provided (not a copy of the argument value); an assignment to the formal parameter inside the callee thus also changes the value in the caller.
In most cases (certain STRING and ARRAY parameters are treated differently, see below for details), VAR_INPUT and VAR_OUTPUT parameters are passed by value. The formal parameter is a copy of the argument value provided. In case of a VAR_INPUT parameter, the caller creates a copy of the argument value and assigns it to the formal parameter before callee execution; in case of a VAR_OUTPUT parameter, the value of the formal parameter is copied to the argument after callee execution has finished.
A variable-length array parameter is always treated like a VAR_IN_OUT parameter irrespective of the section in which it is declared. A variable-length array parameter always contains an implicit reference to an actual array and cannot be omitted.
A STRING or WSTRING parameter without an explicit capacity is always passed by reference. In contrast to variable-length array parameters, however, a STRING or WSTRING parameter without an explicit capacity can be omitted if it is declared in the VAR_INPUT or VAR_OUTPUT section of the callee (in which case an implicitly allocated STRING or WSTRING of the default capacity is used as argument). Note that the caller may provide a STRING or WSTRING with an arbitrary capacity as argument value for a STRING or WSTRING parameter without an explicit capacity.
Note

If a VAR_IN_OUT parameter is a STRING or WSTRING with an explicit capacity, the argument STRING or WSTRING must have the exact same capacity.

If an array with relative addressing is used as an argument for a VAR_INPUT or VAR_OUTPUT parameter, the formal parameter contains (a reference to) an automatically generated copy of the array. Using an array with relative addressing as an argument for a VAR_IN_OUT parameter is prohibited.

Implicit type conversions for call parameters
ST allows certain implicit type conversions for the arguments of a function or method call. Which type conversions are permitted depends on the section that the corresponding formal parameter is declared in (and, for VAR_IN_OUT parameters, on its type).

In case of a VAR_INPUT parameter, the argument's type must either be the same as the formal parameter's type or there must be an implicit type conversion from the argument's type to the formal parameter's type. A rather common example is passing a reference to a derived class instance as an argument for a parameter that expects a base class reference:

CLASS Base
END_CLASS

CLASS Derived EXTENDS Base
END_CLASS

FUNCTION Foo
    VAR_INPUT
        b : REF_TO Base;
    END_VAR
    // ...
    ;
END_FUNCTION

FUNCTION Bar
    VAR_INPUT
        d : REF_TO Derived;
    END_VAR

    Foo(d); // co-variant conversion
END_FUNCTION
In case of a VAR_IN_OUT parameter of a class type, the argument's type must either be the same as the formal parameter's type or a subclass of the formal parameter's type. In case of a VAR_IN_OUT parameter of a non-class type, the argument's type must be the same as the formal parameter's type.

In case of a VAR_OUTPUT parameter, no implicit conversions are supported.

Note

See the corresponding section in the description of the overload resolution for some more technical details.

Binding in case of function block variables and functions with the same name
If there is an accessible function block variable with the same name as one or more accessible functions, the call is bound to the function block (independently of the given arguments). For example, consider the following program fragment:

FUNCTION SomeFunction
    VAR_IN_OUT
        Foo: SomeFunctionBlock;
    END_VAR

    Foo();
END_FUNCTION

FUNCTION_BLOCK SomeFunctionBlock
    ;
END_FUNCTION_BLOCK

FUNCTION Foo
    ;
END_FUNCTION
In this example, the call of Foo() in SomeFunction() is bound to the Foo instance of SomeFunctionBlock.

Constant expressions
Constant expressions evaluate to a fixed value determined at compile time. At certain syntax locations (such as constant declarations, variable and field initializers and initializers of elementary data types), the compiler expects constant expressions and reports a corresponding error if it does not find them.

CONFIGURATION PLC_1
    VAR_GLOBAL CONSTANT
        CONST_LITERAL_INT : INT := 10;
        CONST_SUM_INT : INT := 7 + INT#5;
        CONST_MUL_INT : INT := (7 + 2) * CONST_SUM_INT;
        CONST_TRUE_BOOL : BOOL := TRUE OR FALSE;
        CONST_FALSE_BOOL : BOOL := TRUE AND FALSE XOR NOT TRUE;
        CONST_ADD_REAL : REAL := REAL#0.0 + REAL#1.0;
    END_VAR
    TASK Main(Interval := T#1000ms, Priority := 1);
    PROGRAM P1 WITH Main : SampleProgram;
END_CONFIGURATION

PROGRAM SampleProgram /* name of the program */
    VAR_EXTERNAL CONSTANT
        CONST_LITERAL_INT : INT;
        CONST_SUM_INT : INT;
        CONST_TRUE_BOOL : BOOL;
        CONST_FALSE_BOOL : BOOL;
    END_VAR
    VAR CONSTANT
        alwaysTrue : BOOL := TRUE;
        b : BOOL := alwaysTrue;
    END_VAR
    VAR_TEMP
        t_false : BOOL := CONST_FALSE_BOOL;
        t_true : BOOL := CONST_TRUE_BOOL XOR CONST_FALSE_BOOL;
    END_VAR
    ;
END_PROGRAM
Notice that the compiler treats and accepts only a basic set of operations on elementary data types as constant expressions. Support for string, time and date types is currently restricted to the use of literals or identifiers of constants. A string-type can also be accessed via an index (just like an array).

NAME_OF expression
A NAME_OF expression produces the name of a function, variable, type or member as a string. It is treated as a constant expression and therefore evaluated at compile time and has no runtime effect.

    x := name_of(myGlob);                               // x := 'myGlob'
    x := name_of(x);                                    // x := 'x'
    x := name_of(myFB.y);                               // x := 'y'
    x := name_of(fb1.y);                                // x := 'y'
    x := name_of(MyDatatype);                           // x := 'MyDatatype'
    x := name_of(MyStruct1);                            // x := 'MyStruct1'
    x := name_of(MyStruct1.x);                          // x := 'MyStruct1'
    x := name_of(MyStruct1.innerStruct.x);              // x := 'x'
    x := name_of(Colors);                               // x := 'Colors'
    x := name_of(Colors#GREEN);                         // x := 'GREEN'
    x := name_of(MyClass);                              // x := 'MyClass'
    x := name_of(MyClass.x);                            // x := 'x'
    x := name_of(MyClass.myMethod);                     // x := 'myMethod'
    x := name_of(returnsStruct().x);                    // x := 'x'
    x := name_of(arr[0].x);                             // x := 'x'

    //lookup only in current namespace but not in parent
    x := name_of(MyClass.x);                            // x := 'x'
    x := name_of(NS1.NS2.bar);                          // x := 'bar'
    x := name_of(NS1.NS2);                              // x := 'NS2'