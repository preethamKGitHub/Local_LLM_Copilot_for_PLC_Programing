# Statements

A statement represents a single rule that is to be executed as part of the program. Statements are executed in the order of their declaration.



Assignment
An assignment assigns a new value to a memory location. The memory location is specified with the first expression of the assign statement, the new value with the second expression.

Both expressions must evaluate to the same type, or there must be an implicit conversion from the type of the second expression to the type of first expression.

a := b + c;
Example: Assignment
FUNCTION AddOne : INT
    VAR_INPUT
        a : INT;
    END_VAR
    AddOne := a + 1; (* assigns "a + 1" to "AddOne". *)
END_FUNCTION
Note

The right hand side is evaluated before the left hand side. This can be relevant in cases like refInt^ := foo() where refInt is a global variable and foo changes where refInt points to. The result of foo() is then assigned to the location refInt points to AFTER the call to foo.

Assigning arrays
Note

Restrictions on assigning arrays are based not on the exact type of the array but on structural equality. Structural equality is defined as follows: - The two arrays have the same element type - The two arrays have the same counter - The two arrays have the same count of elements in each dimension

Two arrays can be assigned to each other if they are structurally equal according to these rules irrespective of whether they are named or anonymous.

Assignment attempt
An assignment attempt ?= attempts to assign one object (which may be a reference-type object) to another reference-type object. If the dynamic type of the referenced instance on the right side is assignable to the static-type variable on the left side, the variable on the left side then references the instance on the right side. Otherwise, the left side variable will be NULL. This is similar to what is referred to as a dynamic cast in the C++ language or as in the C# language.

Note

This check can only be performed at runtime, so expect performance drawbacks if used extensively. Usually, the assignment attempt is required when you need to assign a variable to a variable with a more concrete type.

INTERFACE ITop
    // ...
END_INTERFACE
INTERFACE IBottom EXTENDS ITop
    // ...
END_INTERFACE
CLASS C IMPLEMENTS ITop
    // ...
END_CLASS
CLASS D IMPLEMENTS IBottom
    // ...
END_CLASS

FUNCTION foo
    VAR_INPUT
        it : ITop;
    END_VAR
    VAR_TEMP
        ib : IBottom;
    END_VAR

    // some code ...

    ib ?= it;   // is the concrete type of 'it' implementing IBottom?
                // in case, 'it' is of 'CLASS D', then yes! 'ib' then will be valid.
                // in case, 'it' is of 'CLASS C', then no! 'ib' will then be 'NULL'.

    IF ib <> NULL THEN
        ;   // ... some code ...
    END_IF;
END_FUNCTION
Note

It is only applicable for variables of type INTERFACE, CLASS, REF_TO CLASS.
The variable on the left side must be a reference-type variable. The variable on the right side may be a value-type variable if the left side is of the INTERFACE type. A dereference operator (^) need not be applied to an interface-type variable. A REF operator need not be applied to a value-type object if it is assigned to an interface-type variable. This is an implication of IEC61131-3, as an INTERFACE is implicitly a reference type, but my_itf_var ?= my_value_class_var must be supported.
Example: Assignment attempt
The following example shows some more uses of assignment attempt. It omits method declarations in interfaces as they are not important for this illustration.

INTERFACE ITop
END_INTERFACE
INTERFACE ILeft EXTENDS ITop
END_INTERFACE
INTERFACE IRight EXTENDS ITop
END_INTERFACE
INTERFACE IBottom EXTENDS ILeft, IRight // ILeft is only for the purpose of showing multi inheritance using interfaces
END_INTERFACE

INTERFACE IOtherBottom EXTENDS ITop
END_INTERFACE

CLASS A IMPLEMENTS IBottom
END_CLASS
CLASS B EXTENDS A IMPLEMENTS IOtherBottom
    METHOD GetAsARef : REF_TO A
        GetAsARef ?= REF(THIS); // note the difference of the right side in comparison when attempting assignment to an interface-type value
    END_METHOD
    METHOD GetAsOtherBottom : IOtherBottom
        GetAsOtherBottom ?= THIS;
    END_METHOD
END_CLASS

PROGRAM P
    VAR
        b : B;
        bRef : REF_TO B := REF(b);
        a : A;
        aRef : REF_TO A := REF(a);
        ir : IRight;
        ib : IBottom;
        iob : IOtherBottom;
    END_VAR

    bRef ?= aRef; // 'bRef' is NULL because 'aRef' references a type 'A' that is not assignable to 'B'

    bRef := REF(b);
    aRef ?= bRef; // -> type 'B' is assignable to type 'A', so subsequently 'aRef' references 'b' but only methods of 'A' are available; hint: 'aRef := bRef' is equivalent

    bRef ?= aRef; // -> 'bRef' remains unchanged, but now methods of 'B' are available; hint: 'bRef := aRef' is not possible, because statically type 'A' is not assignable to type 'B'

    ir := a;    // 'ir' references 'a' (methods of 'IRight' are available); note that on right side 'REF(a)' is not possible
    aRef ?= ir; // -> 'aRef' references 'a' (methods of type A are available)

    ib ?= ir; // -> 'ib' references 'a', methods of 'IBottom' (and thus 'ITop', 'ILeft', 'IRight') are available

    iob ?= ib; // 'iob' is NULL because 'ib' references a type 'A' that does not implement 'IOtherBottom'

    bRef ?= ib; // 'bRef' is NULL because 'ib' references a type 'A' that is not assignable to 'B'

    iob ?= b; // -> 'iob' references 'b' but only methods of 'IOtherBottom' (and 'ITop') are available

    aRef ?= iob; // 'aRef' references 'b' because type 'B' extends type 'A'

END_PROGRAM
Conditional statement
conditionalStatement:
'IF'
expression
'THEN'
statementList
elsifStatement
elseStatement
'END_IF'
';'
elsifStatement:
'ELSIF'
expression
'THEN'
statementList
elseStatement:
'ELSE'
statementList

A conditional statement (also known as an IF statement) makes a choice between several lists of statements. At most one of the lists is executed.

All expressions of a conditional statement must evaluate to type BOOL.

First the initial expression is evaluated.

If that evaluates to TRUE, the first statement list is executed and after that execution continues after the conditional statement.

If it evaluates to FALSE, all the ELSIF statements are evaluated in declaration order in the same manner. If no condition of any ELSIF statement evaluates to TRUE (or if there are no ELSIF statements), execution continues with the list of statements of the ELSE statement (if it is declared) and then continues after the conditional statement.

Example

FUNCTION IfExample : Int
    VAR_TEMP
        a,b,c : BOOL;
        i : INT;
    END_VAR
    i := 0;
    IF a THEN
        i := 1;
    END_IF;
    // if a is true then i equals 1, otherwise 0

    IF b THEN
        i := 2;
    ELSIF c THEN
        i := 3;
    ELSE
        i := 4;
    END_IF;
    // if b is true then i equals 2
    // if b is false and c is true then i equals 3
    // otherwise i equals 4.
END_FUNCTION
CASE statement
Sometimes we need to evaluate a single expression to decide which code blocks should be executed, i.e. different values of this expression lead to the execution of different blocks. The CASE statement is more convenient than an equivalent chain of IF-THEN-ELSIF-THEN-...-ELSIF-THEN-ELSE statements if the number of choices is large.

caseStatement:
'CASE'
expression
'OF'
statementList
elseStatement
'END_CASE'
';'

As shown in the syntax diagram for the CASE statement, an expression of the integer or enum data type follows the CASE keyword. This expression is used as the "selector", whose value selects which statement list is to be executed. Each statement list is labeled with a "case list". A "case list" consists of one or more "case list elements", each being a constant integer, an enumerated value or a range of constant integers. If the selector expression equals or belongs to the range of one case list element, the corresponding statement list will be executed.

If the selector expression does not match any case list and the keyword ELSE exists in the CASE statement, the statement list following ELSE will be executed.

If the selector expression does not match any case list and there is no ELSE keyword, none of the statement lists will be executed.

The selector expression must be comparable with the case list elements. This requires that all case list elements have the same data type as the selector expression.

Each value in the case list elements is allowed to exist only once. It is not allowed to write overlapping ranges or values existing more than once. For example,

0..5 and 3..6

is not allowed because the values 3, 4 and 5 appear twice.

Example: CASE statement
FUNCTION SwitchInput : INT
    VAR_INPUT
        a : INT := 42;
    END_VAR
    VAR_TEMP
        i : int;
    END_VAR

    CASE a OF           // selector 'a' has value 42
        -32..-12, 15:   // no match
            i := 1;
        -11..3, 19:     // no match
            i := 5;
        4..10, 20..46:  // match, because 'a' is in range 20..46
            i := 10;
        ELSE
            i:= -1;
    END_CASE;
END_FUNCTION
TYPE
    Colors : (Red, Green, Blue);        // definition of the enum Colors
END_TYPE

PROGRAM Demo
    VAR
        color : Colors;
        res : Int;
    END_VAR

    color := Colors#Green;

    CASE color OF                       // selector 'color' has value Colors#Green
        Colors#Red : res := 1;          // no match
        Colors#Green : res := 6;        // match
        Colors#Blue : res := 5;         // no evaluation
    END_CASE;
END_PROGRAM
Iteration statements
Iteration statements can be used to execute a set of statements multiple times. The number of iterations can be restricted by a particular condition.

iterationStatement:
forStatement
whileStatement
repeatStatement

FOR statement
The FOR statement executes a list of statements while a specified expression evaluates to TRUE.

At any point in the FOR statement list, you can break out of the loop by using the EXIT statement or step to the next iteration in the loop by using the CONTINUE statement.

As shown in the syntax diagram, the FOR statement defines an assignStatement as initializer, a TO expression as final value and, optionally, an incrementor expression starting with BY. These expressions must be of the same signed or unsigned integer type ( (U)SINT, (U)INT, (U)DINT or (U)LINT ). IEC 61131-3 does not allow the control variable of the FOR loop to be modified in the body of the loop. This implies that only elementary local variables can be used as the control variable (elements of arrays and structs – as well as global variables – could be modified accidentally in other functions while the loop is being executed).

forStatement:
'FOR'
expression
':='
expression
'TO'
expression
'BY'
expression
'DO'
statementList
'END_FOR'
';'

Note

The FOR statement can be used if the number of iterations is known, for example iterating arrays.

Example 1: FOR statement
FUNCTION Sum: INT
    VAR_INPUT
        lowerBound: INT;
        upperBound: INT;
    END_VAR
    VAR
        i: INT;
    END_VAR

    Sum := 0;
    FOR i := lowerBound TO upperBound BY 1 DO
    // the by-expression can be omitted when it evaluates to 1, simplified as "FOR i := begin TO end DO"
        Sum := Sum + i;
    END_FOR;
    // i will contain the value upperBound + 1
END_FUNCTION
Initializer assignment
The assignStatement in the initializer is executed only once, before entering the loop.

The accessed variable (control variable) must not be altered by any of the repeated statements.

Final value expression
The final value expression is evaluated only once, before entering the loop.

Incrementor value expression
The incrementor value expression is evaluated only once, before entering the loop.

If it is omitted, the incrementor will default to the value 1.

The incrementor value and the final value together specify the termination condition. If the incrementor expression value is less than 0, the loop will terminate when the variable value accessed is less than the final value expression. Otherwise it will terminate when the variable value accessed is greater than the final value.

FOR i := 1 TO 5 BY 1 DO will result in an exit condition of i > 5
FOR i := 10 TO 5 BY -1 DO will result in an exit condition of i < 5
The earlier example of summation using iteration with ascending order is equivalent to the following code using iteration with descending order.

Example 2: FOR statement
FUNCTION Sum: INT
    VAR_INPUT
        lowerBound: INT;
        upperBound: INT;
    END_VAR
    VAR
        i: INT;
    END_VAR

    Sum := 0;
    FOR i := upperBound TO lowerBound BY -1 DO
        Sum := Sum + i;
    END_FOR;
    // i will contain the value lowerBound - 1
END_FUNCTION
WHILE statement
The WHILE statement executes a list of statements while a specified Boolean expression evaluates to TRUE. Because this expression is evaluated before each execution of the loop, a WHILE loop executes zero or more times.

At any point within the WHILE statement list, you can break out of the loop by using the EXIT statement, or step to the next expression evaluation by using the CONTINUE statement.

whileStatement:
'WHILE'
expression
'DO'
statementList
'END_WHILE'
';'

Note

The WHILE statement can be used if the number of iterations is not known.

Example: WHILE statement
FUNCTION Loops
    VAR_TEMP
        x : INT := 0;
    END_VAR

    WHILE x < 10 DO
        x := x + 1;
    END_WHILE;
    // x will contain the value 10
END_FUNCTION
REPEAT statement
The REPEAT statement executes a list of statements until a specified Boolean expression evaluates to TRUE. Because this expression is evaluated after each execution of the loop, a REPEAT loop executes one or more times.

At any point within the REPEAT statement list, you can break out of the loop by using the EXIT statement, or step to the next expression evaluation by using the CONTINUE statement.

repeatStatement:
'REPEAT'
statementList
'UNTIL'
expression
'END_REPEAT'
';'

Note

The REPEAT statement can be used if the number of iterations is not known and the loop must be executed at least once.

Example: REPEAT statement
FUNCTION Loops
    VAR_TEMP
        x : INT := 0;
    END_VAR

    REPEAT
        x := x + 1;
        UNTIL x >= 10
    END_REPEAT;
    // x will contain the value 10
END_FUNCTION
Jump statements
Jump statements can be used to interrupt the control flow of the program manually.

jumpStatement:
continueStatement
exitStatement
returnStatement

CONTINUE statement
The CONTINUE statement passes control to the next iteration of the enclosing loop in which it appears.

continueStatement:
'CONTINUE'
';'

Note

A continue statement may only be used inside a loop.

Example: CONTINUE statement
FUNCTION SkipIterations
    VAR_TEMP
        x: INT := 0;
        y: INT := 0;
    END_VAR

    WHILE x < 10 DO
        x := x + 1;
        IF y >= 5 THEN
            CONTINUE;
        END_IF;
        y := y + 1;
    END_WHILE;
    // x will contain the value 10, y will contain the value 5
END_FUNCTION
EXIT statement
The EXIT statement terminates the enclosing loop in which it appears.

exitStatement:
'EXIT'
';'

Note

An exit statement may only be used inside a loop.

Example: EXIT statement
FUNCTION BreakIterations
    VAR_TEMP
        x: INT := 0;
        y: INT := 0;
    END_VAR

    WHILE x < 10 DO
        x := x + 1;
        IF y >= 5 THEN
            EXIT;
        END_IF;
        y := y + 1;
    END_WHILE;
    // x will contain the value 6, y will contain the value 5
END_FUNCTION
RETURN statement
The RETURN statement terminates execution of the program organization unit in which it appears.

returnStatement:
'RETURN'
';'

Note

A return statement may only be used inside the following POU: - Program - Function - Method

Example: RETURN statement
PROGRAM Caller
    VAR
        res : INT;
    END_VAR
    res := callee(in := 5);
END_PROGRAM

FUNCTION callee : INT
    VAR_INPUT
        in : INT;
    END_VAR
    IF in >= 5 THEN
        callee := 23;
        RETURN;
    END_IF;
    callee := 42;
END_FUNCTION
// res will contain the value 23, not 42