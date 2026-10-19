# OOP overview
ST features the "object oriented programming" paradigm, which can help you to structure your code in an understandable and more extensible way. At its core, OOP is built around objects that encapsulate data and methods that operate on this data.

## OOP by topics.

	1. Classes
	2. Methods
	3. SUPER Calls
	4. Class Inheritance
	5. Method Overriding
	6. Interfaces
	7. Copy Functions

## Class
    Class declaration
    A class is the basic construct to support object-oriented programming in ST. It encapsulates a set of data (field) and behaviors (methods) that belong together as a logical unit. The fields and methods are members of the class. More detailed information about object-oriented programming can be found here.

        Example: Class
        CLASS Motor

        END_CLASS

        CLASS Motor
            VAR PRIVATE
                isRunning : BOOL;
            END_VAR
        END_CLASS

### Class variables

        A VAR...END_VAR construct, if required, specifying the names and types of the variables of the class. Each variable can have an access modifier such as PUBLIC, PRIVATE, INTERNAL, or PROTECTED. If omitted, the default is PROTECTED. Variables can only be declared in the VAR section. The VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT and VAR_TEMP sections are not allowed. The derived class cannot declare a variable with the same name as a variable already contained in its base class, whether defined there or inherited. This rule does not apply if the variable contained in the base class is inaccessible in the derived class, as shown in the following example.


        NAMESPACE NS1
            CLASS C1
                VAR INTERNAL
                    C1_FIELD : BOOL;
                END_VAR
                VAR PRIVATE
                    C1_PRIVATE_FIELD : BOOL;
                END_VAR
            END_CLASS

            CLASS C2 EXTENDS C1
                VAR PUBLIC
                    C1_FIELD : BOOL; // Error, because C1_FIELD from the base class is defined as INTERNAL within the same namespace
                    C1_PRIVATE_FIELD : BOOL; // OK, because C1_PRIVATE_FIELD from the base class is defined as PRIVATE and therefore inaccessible in the derived class
                END_VAR
            END_CLASS
        END_NAMESPACE

        NAMESPACE NS1
            CLASS C1
                VAR INTERNAL
                    C1_FIELD : BOOL;
                END_VAR
            END_CLASS
        END_NAMESPACE

        USING NS1;

        CLASS C2 EXTENDS NS1.C1
            VAR PUBLIC
                C1_FIELD : BOOL; // OK, because C1_FIELD from the base class is defined as INTERNAL in a different namespace and therefore inaccessible here
            END_VAR
        END_CLASS

### Class constants

    Class constants are constant fields inside a class that are declared by adding the CONSTANT keyword to a VAR section in the class. The visibility of these constants can be controlled using access modifiers. If an access modifier is used, the syntax is: VAR CONSTANT ACCESS-MODIFIER (e.g. VAR CONSTANT PUBLIC).

        CLASS ProcessConstants
            VAR CONSTANT PUBLIC
                ProcessValue1 : REAL := REAL#123.4;
                ProcessValue2 : DWORD := DWORD#16#F00D;
            END_VAR
            VAR CONSTANT PRIVATE
                InternalProcessValue : REAL := REAL#567.8;
            END_VAR

            METHOD PRIVATE Foo
                IF ProcessValue1 > InternalProcessValue THEN
                ;
                END_IF;
            END_METHOD
        END_CLASS

        FUNCTION_BLOCK Compare
            VAR_INPUT
                actual : REAL;
            END_VAR
            VAR
                constants : ProcessConstants;
            END_VAR

            IF actual > constants.ProcessValue1 THEN
                ;
            END_IF;
        END_FUNCTION_BLOCK

    Class constants behave exactly like global constants, except that their accessibility is restricted by the visibility of the class field declaration.

## Method
    Method declaration
    A method is a POU similar to a function, but it is only callable with an instance of the declaring class or function block.

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

        CLASS Motor
            VAR PRIVATE
                isRunning : BOOL;
            END_VAR

            METHOD PUBLIC Start
                isRunning := TRUE;
            END_METHOD

            METHOD PUBLIC Stop
                isRunning := FALSE;
            END_METHOD
        END_CLASS







## SUPER calls
    Sometimes it would be useful to be able to call a method that is overridden, for example if you want to add additional functionality before or after the base code.

    CLASS MotorControl
        VAR
            MotorId: Int;
        END_VAR

        METHOD PUBLIC Start
            // <Code that performs motor startup>
            ;
        END_METHOD

        METHOD PUBLIC Stop
            // <Code that performs motor stop>
            ;
        END_METHOD
    END_CLASS
    Say we want to know when a motor is started or stopped. One way of performing this task is to use a variant of the so-called decorator pattern. Instead of using MotorControl directly, use LoggingMotorControl, which calls into additional functions before actually starting/stopping the motor.

        CLASS LoggingMotorControl EXTENDS MotorControl
            METHOD PUBLIC OVERRIDE Start
                // <Code that runs prior to actual motor startup>
                Logger.LogMotorStart(this.MotorId);
                SUPER.Start();
                // <Code that runs after actual motor startup>
            END_METHOD

            METHOD PUBLIC OVERRIDE Stop
                // <Code that runs prior to actual motor stop>
                Logger.LogMotorStop(this.MotorId);
                SUPER.Stop();
                // <Code that runs after to actual motor stop>
            END_METHOD
        END_CLASS

        NAMESPACE Logger
            FUNCTION LogMotorStart
                VAR_INPUT motorId: INT; END_VAR
                ;// <Code that performs the logging>
            END_FUNCTION
            FUNCTION LogMotorStop
                VAR_INPUT motorId: INT; END_VAR
                ;// <Code that performs the logging>
            END_FUNCTION
        END_NAMESPACE

#### Abstract classes and abstract methods
Sometimes it can be useful to declare a class that cannot be instantiated and is only to be used as a base class for other classes. This can be achieved by annotating the class as ABSTRACT. An abstract class should have at least one abstract method, which declares the method name, the parameters and the return value but has no concrete implementation (code body). An abstract method may only be declared in an abstract class.

In contrast to an interface, an abstract class can also contain fields and non-abstract methods if necessary.

An abstract class behaves in the same way as non-abstract classes regarding inheritance. If a non-abstract class is directly derived from an abstract class, however, this non-abstract class must override all the abstract methods it inherits directly (from the abstract parent class) or indirectly (from the abstract grandparent class and so on). It must provide concrete implementation.

For example, there are two variants of motor control, each of which needs its unique code to start or stop the motor. Both variants need the restart method, which calls their respective start and stop methods. In this case, we can declare an abstract base class MotorControl:

CLASS ABSTRACT MotorControl
    VAR
        MotorId: Int;
    END_VAR

    METHOD PUBLIC ABSTRACT Start END_METHOD
    METHOD PUBLIC ABSTRACT Stop END_METHOD

    METHOD PUBLIC FINAL Restart
        this.Stop();
        this.Start();
    END_METHOD

END_CLASS
The MotorControl class cannot be instantiated and its non-abstract derived classes must implement the methods Start and Stop, otherwise the compiler will issue an error.

CLASS MotorControlVariant1 EXTENDS MotorControl
    METHOD PUBLIC OVERRIDE Start
        ; //Start code for variant 1
    END_METHOD
    METHOD PUBLIC OVERRIDE Stop
        ; //Stop code for variant 1
    END_METHOD
END_CLASS

CLASS MotorControlVariant2 EXTENDS MotorControl
    METHOD PUBLIC OVERRIDE Start
        ; //Start code for variant 2
    END_METHOD
    METHOD PUBLIC OVERRIDE Stop
        ; //Stop code for variant 2
    END_METHOD
END_CLASS
Please note the Restart method, which uses a variant of the template method pattern.

By referring to objects of different concrete classes, an abstract class reference can be used to call different implementations of the abstract method. In this way, polymorphism is achieved.

PROGRAM MyProgram
    VAR
        MotorControlVariant1_Inst: MotorControlVariant1;
        MotorControlVariant2_Inst: MotorControlVariant2;
        MotorControlRef: REF_TO MotorControl;
    END_VAR

    MotorControlVariant1_Inst.Start();
    MotorControlVariant2_Inst.Start();

    MotorControlRef:=REF(MotorControlVariant1_Inst);
    MotorControlRef^.Start();   //Calls the start code for variant 1
    MotorControlRef^.Restart(); //Calls the stop and start code for variant 1

    MotorControlRef:=REF(MotorControlVariant2_Inst);
    MotorControlRef^.Start();   //Calls the start code for variant 2
    MotorControlRef^.Restart(); //Calls the stop and start code for variant 2
END_PROGRAM




## Class inheritance
The inheritance relationship between classes is one of the core concepts of object-oriented programming. It makes it possible to derive a new class from an existing one to form a hierarchy. This can be useful for adding new functionality and reusing the existing data structure and logic.

In ST, a class can be derived from one other class by using the keyword EXTENDS. Note that deriving from more than one base class (multi-inheritance) is not supported in ST.

Classes can be annotated with the FINAL keyword, which prevents the class from being inherited by other classes. Any attempt to extend a final class will produce an error message.

If a class SubClass extends a class BaseClass, the following rules apply:

    1. SubClass inherits all methods and fields of BaseClass, except for
        PRIVATE methods/fields
        INTERNAL methods/fields if SubClass is in a different namespace to BaseClass
    2. SubClass can add additional methods and fields
    3. Cyclic inheritance chains are forbidden (i.e. a class A cannot extend a class B if B extends A or a subclass of A)
    4. Overloading across the inheritance hierarchy is allowed

### Basic example
        CLASS BaseClass
            VAR
                state : INT;    // Available in 'SubClass'
            END_VAR
            VAR PRIVATE
                inner_state : INT;  // Not available in 'SubClass'
            END_VAR
            METHOD Test
                inner_state := 10;
            END_METHOD
            METHOD PRIVATE InnerTest  // Not available in 'SubClass'
                ;
            END_METHOD
        END_CLASS

        CLASS SubClass EXTENDS BaseClass
            VAR
                additional_state : INT;    // Inherited by 'SubClass'
            END_VAR
            METHOD AdditionalTest
                THIS.Test();    // Access to method of 'BaseClass'
                state := 10;    // Access to fields of 'BaseClass'
                additional_state := 20;
            END_METHOD
        END_CLASS

        CLASS FINAL SealedSubClass EXTENDS BaseClass
            // 'SealedSubClass' is final and cannot be extended.
        END_CLASS


## Method overriding
    Within an inheritance hierarchy, a method in a subclass may override a public, protected or internal (if in the same namespace) method in its base class or higher base classes using the OVERRIDE keyword. Methods can be overridden multiple times.

    Methods can be annotated with the FINAL keyword, which prevents the method from being overridden in any subclasses. Any attempt to override a final method will produce an error message.

    Since a PRIVATE method cannot be overridden anyway, annotating it as final is treated as an error.

        CLASS BaseClass
            METHOD PUBLIC ExampleMethod : INT
                ExampleMethod := 111;
            END_METHOD

            METHOD PUBLIC FINAL SealedMethod
                ; // 'SealedMethod' is final and cannot be overridden in a subclass.
            END_METHOD
        END_CLASS

        CLASS SubClass EXTENDS BaseClass
            METHOD PUBLIC OVERRIDE ExampleMethod : INT
                ExampleMethod := 222;
            END_METHOD
        END_CLASS

    When performing a call to such a method, the dynamic type of the class instance determines which method is invoked.

        FUNCTION Example
            VAR_EXTERNAL
                baseClassInstance : BaseClass;
                subClassInstance : SubClass;
            END_VAR
            VAR_TEMP
                reference : REF_TO BaseClass;
                result : INT;
            END_VAR
            reference := REF(baseClassInstance);
            result := reference^.ExampleMethod();    // yields 111

            reference := REF(subClassInstance);
            result := reference^.ExampleMethod();    // yields 222
        END_FUNCTION

    A method overriding a method of a base class must have the exact same access modifier, otherwise overriding will produce an error.

        CLASS BaseClass
            METHOD PUBLIC ExampleMethod
                ;
            END_METHOD
        END_CLASS

        CLASS SubClass1 EXTENDS BaseClass
            METHOD PUBLIC OVERRIDE ExampleMethod   // Right
                ;
            END_METHOD
        END_CLASS

        CLASS SubClass2 EXTENDS BaseClass
            METHOD OVERRIDE ExampleMethod  // Wrong, method access modifier is omitted and by default PROTECTED, which is different from the overridden base method
                ;
            END_METHOD
        END_CLASS
    The overriding method must be compatible with the method it overrides.

    Virtual Method Declaration Compatibility
    A method declaration is a valid override of its base method (or a valid implementation of an interface method) if and only if all of the following conditions are met:

        1. it has the same signature
        2. it has the same parameter names
        3. it has a compatible return type
    The parameter names and the return type are not part of the signature, but must be compatible for predictable behavior. The parameter names must match to avoid ambiguities when invoking a method with a formal call.

        CLASS BaseClass
            METHOD PUBLIC ExampleMethod
                VAR_INPUT
                    i : INT;
                END_VAR
                ;
            END_METHOD
        END_CLASS

        CLASS SubClass EXTENDS BaseClass
            METHOD PUBLIC OVERRIDE ExampleMethod
                VAR_INPUT
                    j : INT; // wrong, because now it is unclear which method should be called in ExampleFunction
                END_VAR
                ;
            END_METHOD
        END_CLASS

        FUNCTION ExampleFunction
            VAR_INPUT
                objectRef : REF_TO SubClass;
            END_VAR
            objectRef^.ExampleMethod(i := 1);
        END_FUNCTION

    The return type of the overriding method is compatible with the return type of the method it overrides:

    1. If the return type of the original method is a REF_TO a class type, the return type of the overriding method may be either a REF_TO the same class or a REF_TO a class that extends this class.
    2. If the return type of the original method is an interface type, the return type of the overriding method may be the same interface, an interface that extends this interface or a REF_TO a class that implements this interface.
    3. In all other cases, the return type of the overriding method must be the exact same type as the return type of the original method.

### Static vs dynamic binding
    Both overloading and overriding allow multiple declarations of a method with the same name. The compiler then decides which method is actually called based on the call context (parameters, class instance).

    These two features do not though bind in the same way:

        1. Overloading uses static binding, meaning the static type of a class instance determines the set of available methods.
        2. Overriding uses dynamic binding, meaning the dynamic type of a class instance determines which method is called.

    complex scenarios can be constructed in combination with implicit type conversion:

        FUNCTION Example
            VAR_EXTERNAL
                baseClassInstance : BaseClass;
                subClassInstance : SubClass;
            END_VAR
            VAR_TEMP
                baseClassRef : REF_TO BaseClass;
                subClassRef : REF_TO SubClass;
                result : Int;
            END_VAR
            // static type: BaseClass, dynamic type: BaseClass
            baseClassRef := REF(baseClassInstance);
            result := baseClassRef^.Overloaded(REAL#5.0);   // yields 1
            result := baseClassRef^.Overloaded(INT#3);      // yields 1

            // static type: BaseClass, dynamic type: SubClass
            baseClassRef := REF(subClassInstance);
            result := baseClassRef^.Overloaded(REAL#5.0);   // yields 22
            result := baseClassRef^.Overloaded(INT#3);      // yields 22

            // static type: SubClass, dynamic type: SubClass
            subClassRef := REF(subClassInstance);
            result := subClassRef^.Overloaded(REAL#5.0);    // yields 22
            result := subClassRef^.Overloaded(INT#3);       // yields 333
        END_FUNCTION

        CLASS BaseClass
            METHOD PUBLIC Overloaded : INT
                VAR_INPUT
                    in : REAL;
                END_VAR
                Overloaded := 1;
            END_METHOD
        END_CLASS

        CLASS SubClass EXTENDS BaseClass
            METHOD PUBLIC OVERRIDE Overloaded : INT
                VAR_INPUT
                    in : REAL;
                END_VAR
                Overloaded := 22;
            END_METHOD

            METHOD PUBLIC Overloaded : INT
                VAR_INPUT
                    in : INT;
                END_VAR
                Overloaded := 333;
            END_METHOD
        END_CLASS


## Interface
    Interfaces allow you to express a contract that classes must implement. This enables you to write code that depends on abstractions rather than concrete implementations, which can help you to decouple your software and increase maintainability.

### Interface declaration
    An interface is declared using the INTERFACE keyword and can contain any number of METHOD prototypes. A METHOD prototype is very similar to a normal METHOD, but may not specify implementation details such as VAR_TEMP or a code body. Interfaces can extend any number of other interfaces using the EXTENDS keyword as long as the hierarchy contains no cycles.

        INTERFACE SuperInterface
            METHOD MyMethod : INT
                VAR_INPUT
                    a, b : INT;
                END_VAR
            END_METHOD
        END_INTERFACE

        INTERFACE DerivedInterface EXTENDS SuperInterface
            METHOD AnotherMethod : INT
            END_METHOD
        END_INTERFACE

Note: The variable initialization of an interface method is only allowed for VAR_INPUT section. E.g.

        INTERFACE I
            METHOD MyMethod : INT
                VAR_INPUT
                    a : INT := 2;
                END_VAR
            END_METHOD
        END_INTERFACE

### Implementing interfaces
A class can implement any number of interfaces using the IMPLEMENTS keyword. In doing this, the class must implement all methods defined by all implemented interfaces.

Note

An implementation of an interface method must fullfill the same requirements as overriding methods.

        CLASS MyImplementation IMPLEMENTS DerivedInterface
            METHOD PUBLIC MyMethod : INT        // Interface methods must be implement as PUBLIC
                VAR_INPUT
                    a, b : INT;
                END_VAR
                VAR_TEMP
                    temp : INT;     // You can add temporary variables and code as required.
                END_VAR
                MyMethod := 10;
            END_METHOD

            // Error: Class does not implement all interfaces. 'AnotherMethod' is missing.
        END_CLASS

### Using interfaces
Variables that are typed as 'interface' are initialized with NULL until a compatible variable or instance is assigned. Note that a compatible variable is a variable whose type is a subtype of the variable to which it is assigned.

Note: A variable typed as 'interface' cannot be used to initialize another variable. It can be only assigned in the code section.

        CONFIGURATION Default
            PROGRAM P1 : Entry;
            VAR_GLOBAL
                o1 : O := (i := 1);
                o2 : O := (i := 2);
                i1 : I := o1;
                i2 : I := o2;
                res_foo1 : INT;
                res_foo2 : INT;
                res_foo3 : INT;
                res_foo4 : INT;
            END_VAR
        END_CONFIGURATION

        PROGRAM Entry
            VAR_EXTERNAL
                o1 : O;
                o2 : O;
                i1 : I;
                i2 : I;
                res_foo1 : INT;
                res_foo2 : INT;
                res_foo3 : INT;
                res_foo4 : INT;
            END_VAR

            res_foo1 := i1.foo();
            res_foo2 := i2.foo();

            i1 := o2;
            res_foo3 := i1.foo();

            i2 := i1;
            res_foo4 := i2.foo();

        END_PROGRAM

        INTERFACE I
            METHOD foo : INT END_METHOD
        END_INTERFACE

        CLASS O IMPLEMENTS I
            VAR PUBLIC
                i : INT;
            END_VAR

            METHOD PUBLIC foo : INT
                foo := i;
            END_METHOD

        END_CLASS

### Basic example
        The following example declares an 'ICalculator' INTERFACE that defines a 'Calc' method with two INT variables.

        INTERFACE ICalculator
            METHOD Calc : INT
                VAR_INPUT
                    a, b : INT;
                END_VAR
            END_METHOD
        END_INTERFACE

        CLASS AddCalculator IMPLEMENTS ICalculator
            METHOD PUBLIC Calc : INT
                VAR_INPUT
                    a, b : INT;
                END_VAR
                Calc := a + b;
            END_METHOD
        END_CLASS

        CLASS SubCalculator IMPLEMENTS ICalculator
            METHOD PUBLIC Calc : INT
                VAR_INPUT
                    a, b : INT;
                END_VAR
                Calc := a - b;
            END_METHOD
        END_CLASS

        FUNCTION Func : INT
            VAR_INPUT
                impl : ICalculator;
            END_VAR
            // Result could be 8 or -2, depending on which implementation of 'ICalculator' is specified.
            Func := impl.Calc(3, 5);
        END_FUNCTION

        PROGRAM Prog
            VAR
                addCalc : AddCalculator;
                subCalc : SubCalculator;
                calc : ICalculator := addCalc;  // Concrete implementation is bound to interface
            END_VAR

            Func(calc);
        END_PROGRAM

### Example with initial values
    The following example declares:

    an INTERFACE 'I' which defines a method 'M' with an INT variable which has an initial value;
    a CLASS 'C' which implements the INTERFACE. The initial value of the implemented method 'M' is different from that of the INTERFACE.
    
        INTERFACE I
            METHOD M : INT
                VAR_INPUT
                    a : INT := 10;  // Initialize the variable in INTERFACE
                END_VAR
            END_METHOD
        END_INTERFACE

        CLASS C IMPLEMENTS I
            METHOD PUBLIC M : INT
                VAR_INPUT
                    a : INT := 20;  // Initialize the variable in CLASS
                END_VAR
                M := a + 1;
            END_METHOD
        END_CLASS

        PROGRAM Prog
            VAR
                c : C;
                i : I := c;
                result : INT;
            END_VAR

            result := i.m();   // In this case, the initial value comes from INTERFACE because the declaration type of i is INTERFACE. Then the result is '11'.
            result := c.m();   // Similarly, the initial value comes from CLASS and the result is '21'.
        END_PROGRAM


## Copy Functions
When copying instances of classes, the ST Compiler emits calls to a compiler-generated copy function. The copy function copies all members of the respective class (also private ones). Note, however, that only the members of the (static) type of the target variable are copied (see the example below).

The copy functions are automatically created per class declaration at the point of the respective declaration.

CONFIGURATION CFG
    PROGRAM P1 : PRG;
    VAR_GLOBAL
        b_glob: Base;
        d_glob: Derived;
    end_Var
END_CONFIGURATION

PROGRAM PRG ; END_PROGRAM

CLASS Base
    VAR PUBLIC
        pub_base: INT;
    END_VAR
    VAR PRIVATE
        priv_base: INT;
    END_VAR
END_CLASS

CLASS Derived EXTENDS Base
    VAR PUBLIC
        pub_derived: INT;
    END_VAR
    VAR PRIVATE
        priv_derived: INT;
    END_VAR
END_CLASS

FUNCTION SomeFunction
    VAR_IN_OUT
        b_io1, b_io2: base;
    END_VAR
    VAR_EXTERNAL
        b_glob: Base;
        d_glob: Derived;
    END_VAR

    // type of the target variable: Base => copied members: { pub_base, priv_base }
    b_glob := b_glob;

    // type of the target variable: Base => copied members: { pub_base, priv_base }
    // since the type of the variable on the right hand side differs, the compiler emits a warning
    // (partial assignment)
    b_glob := d_glob;

    // type of the target variable: (REF_TO) Base => copied members: { pub_base, priv_base }
    // since the target variable may also point to a Derived instance, the compiler emits a
    // warning (possible partial assignment)
    b_io1 := b_glob;

    // type of the target variable: Base => copied members: { pub_base, priv_base }
    // since the variable on the right hand side may also point to a Derived instance, the compiler
    // emits a warning (possible partial assignment)
    b_glob := b_io1;

    // type of the target variable: (REF_TO) Base => copied members: { pub_base, priv_base }
    // since both variables may also point to Derived instances, the compiler emits a warning
    // (possible partial assignment)
    b_io1 := b_io2;
END_FUNCTION

FUNCTION SomeOtherFunction
    VAR_INPUT
        b_ref_1: REF_TO Base;
        b_ref_2: REF_TO Base;
    END_VAR
    VAR_EXTERNAL
        b_glob: Base;
    END_VAR

    // type of the target variable: (REF_TO) Base => copied members: { pub_base, priv_base }
    // since the target variable may also point to a Derived instance, the compiler emits a warning
    // (possible partial assignment)
    b_ref_1^ := b_glob;

    // type of the target variable: Base => copied members: { pub_base, priv_base }
    // since the variable on the right hand side may also point to a Derived instance, the compiler
    // emits a warning (possible partial assignment)
    b_glob := b_ref_1^;

    // type of the target variable: (REF_TO) Base => copied members: { pub_base, priv_base }
    // since both variables may also point to Derived instances, the compiler emits a warning
    // (possible partial assignment)
    b_ref_1^ := b_ref_2^;
END_FUNCTION

FUNCTION_BLOCK SomeFunctionBlock
    VAR_INPUT
        b_in: Base;
    END_VAR
    VAR_OUTPUT
        b_out: Base;
        d_out: Derived;
    END_VAR
    VAR_EXTERNAL
        b_glob: Base;
    END_VAR

    // type of the target variable: Base => copied members: { pub_base, priv_base }
    b_glob:= b_in;
END_FUNCTION_BLOCK

FUNCTION_BLOCK Caller
    VAR
        fbInstance: SomeFunctionBlock;
    END_VAR
    VAR_IN_OUT
        b_io1, b_io2: Base;
    END_VAR
    VAR_EXTERNAL
        b_glob: Base;
        d_glob: Derived;
    END_VAR

    // type of the target variable: Base => copied members: { pub_base, priv_base }
    fbInstance(b_in := b_glob);

    // type of the target variable: Base => copied members: { pub_base, priv_base }
    // since the type of the given argument differs, the compiler emits a warning (partial
    // assignment)
    fbInstance(b_in := d_glob);

    // type of the target variable: Base => copied members: { pub_base, priv_base }
    // since the argument could also point to a Derived instance, the compiler emits a warning
    // (possible partial assignment)
    fbInstance(b_in := b_io1);

    // type of the target variable: (REF_TO) Base => copied members: { pub_base, priv_base }
    // since the target variable could also point to a Derived instance, the compiler emits a
    // warning (possible partial assignment)
    fbInstance(b_out => b_io1);

    // since both parameters are VAR_IN_OUT parameters, only references are passed to the callee
    // => no members are copied
    SomeFunction(b_io1, b_io2);
END_FUNCTION_BLOCK