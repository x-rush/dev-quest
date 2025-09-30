# TypeScript 速查手册

## 基础类型

### 基本类型

```typescript
// 布尔值
let isDone: boolean = false;

// 数字
let decimal: number = 6;
let hex: number = 0xf00d;
let binary: number = 0b1010;
let octal: number = 0o744;
let big: bigint = 100n;

// 字符串
let color: string = "blue";
let fullName: string = `Bob Bobbington`;
let age: number = 37;
let sentence: string = `Hello, my name is ${fullName}.
I'll be ${age + 1} years old next month.`;

// 数组
let list: number[] = [1, 2, 3];
let list2: Array<number> = [1, 2, 3];

// 元组
let x: [string, number] = ["hello", 10];

// 枚举
enum Color {
  Red,
  Green,
  Blue,
}
let c: Color = Color.Green;

// Any
let notSure: any = 4;
notSure = "maybe a string instead";
notSure = false;

// Void
function warnUser(): void {
  console.log("This is a warning message");
}

// Null 和 Undefined
let u: undefined = undefined;
let n: null = null;

// Never
function error(message: string): never {
  throw new Error(message);
}

// Object
declare function create(o: object | null): void;
create({ prop: 0 }); // OK
create(null); // OK
create(42); // Error
create("string"); // Error
create(false); // Error
create(undefined); // Error
```

### 类型断言

```typescript
// 尖括号语法
let someValue: any = "this is a string";
let strLength: number = (<string>someValue).length;

// as 语法
let someValue: any = "this is a string";
let strLength: number = (someValue as string).length;

// 非空断言
function liveDangerously(x?: number | null) {
  // No error
  console.log(x!.toFixed());
}
```

## 接口 (Interfaces)

### 基础接口

```typescript
interface Person {
  name: string;
  age: number;
}

function greet(person: Person) {
  return "Hello, " + person.name;
}

let user = { name: "Alice", age: 30 };
console.log(greet(user));
```

### 可选属性

```typescript
interface SquareConfig {
  color?: string;
  width?: number;
}

function createSquare(config: SquareConfig): { color: string; area: number } {
  return {
    color: config.color || "white",
    area: config.width ? config.width * config.width : 20,
  };
}
```

### 只读属性

```typescript
interface Point {
  readonly x: number;
  readonly y: number;
}

let p1: Point = { x: 10, y: 20 };
p1.x = 5; // Error!

// ReadonlyArray
let a: number[] = [1, 2, 3, 4];
let ro: ReadonlyArray<number> = a;
ro[0] = 12; // Error!
ro.push(5); // Error!
ro.length = 100; // Error!
a = ro; // Error!
```

### 函数类型

```typescript
interface SearchFunc {
  (source: string, subString: string): boolean;
}

let mySearch: SearchFunc = function (source: string, subString: string) {
  return source.search(subString) > -1;
};
```

### 可索引类型

```typescript
interface StringArray {
  [index: number]: string;
}

let myArray: StringArray = ["Bob", "Fred"];

interface NumberDictionary {
  [index: string]: number;
  length: number; // 可以，length是number
  name: string; // 错误，`name`的类型不是number的类型
}
```

### 类类型

```typescript
interface ClockInterface {
  currentTime: Date;
  setTime(d: Date): void;
}

class Clock implements ClockInterface {
  currentTime: Date = new Date();
  setTime(d: Date) {
    this.currentTime = d;
  }
  constructor(h: number, m: number) {}
}
```

### 扩展接口

```typescript
interface Shape {
  color: string;
}

interface Square extends Shape {
  sideLength: number;
}

let square = {} as Square;
square.color = "blue";
square.sideLength = 10;
```

### 混合类型

```typescript
interface Counter {
  (start: number): string;
  interval: number;
  reset(): void;
}

function getCounter(): Counter {
  let counter = (function (start: number) {}) as Counter;
  counter.interval = 123;
  counter.reset = function () {};
  return counter;
}
```

## 函数

### 函数类型

```typescript
// 命名函数
function add(x: number, y: number): number {
  return x + y;
}

// 函数表达式
let myAdd = function (x: number, y: number): number {
  return x + y;
};

// 箭头函数
let myAdd = (x: number, y: number): number => {
  return x + y;
};

// 完整函数类型
let myAdd: (x: number, y: number) => number = function (
  x: number,
  y: number
): number {
  return x + y;
};
```

### 可选参数和默认参数

```typescript
// 可选参数
function buildName(firstName: string, lastName?: string) {
  if (lastName) {
    return firstName + " " + lastName;
  } else {
    return firstName;
  }
}

// 默认参数
function buildName(firstName: string, lastName = "Smith") {
  return firstName + " " + lastName;
}
```

### 剩余参数

```typescript
function buildName(firstName: string, ...restOfName: string[]) {
  return firstName + " " + restOfName.join(" ");
}

let employeeName = buildName("Joseph", "Samuel", "Lucas", "MacKinzie");
```

### 函数重载

```typescript
function pickCard(x: {suit: string; card: number; }[]): number;
function pickCard(x: number): {suit: string; card: number; };
function pickCard(x: any): any {
    // Check to see if we're working with an object/array
    // if so, they gave us the deck and we'll pick the card
    if (typeof x == "object") {
        let pickedCard = Math.floor(Math.random() * x.length);
        return pickedCard;
    }
    // Otherwise just let them pick the card
    else if (typeof x == "number") {
        let pickedSuit = Math.floor(x / 13);
        return { suit: suits[pickedSuit], card: x % 13 };
    }
}
```

## 泛型

### 基础泛型

```typescript
// 泛型函数
function identity<T>(arg: T): T {
  return arg;
}

let output = identity<string>("myString");
let output = identity("myString"); // 类型推断

// 泛型接口
interface GenericIdentityFn {
  <T>(arg: T): T;
}

let myIdentity: GenericIdentityFn = identity;

// 泛型类
class GenericNumber<T> {
  zeroValue: T;
  add: (x: T, y: T) => T;
}

let myGenericNumber = new GenericNumber<number>();
myGenericNumber.zeroValue = 0;
myGenericNumber.add = function (x, y) {
  return x + y;
};
```

### 泛型约束

```typescript
interface Lengthwise {
  length: number;
}

function loggingIdentity<T extends Lengthwise>(arg: T): T {
  console.log(arg.length); // 现在我们知道arg具有.length属性
  return arg;
}

// 在泛型约束中使用类型参数
function getProperty<T, K extends keyof T>(obj: T, key: K) {
  return obj[key];
}

let x = { a: 1, b: 2, c: 3, d: 4 };
getProperty(x, "a"); // 正确
getProperty(x, "m"); // 错误: 参数'm'不存在于'{ a: number; b: number; c: number; d: number; }'
```

## 类

### 基础类

```typescript
class Greeter {
  greeting: string;

  constructor(message: string) {
    this.greeting = message;
  }

  greet() {
    return "Hello, " + this.greeting;
  }
}

let greeter = new Greeter("world");
```

### 继承

```typescript
class Animal {
  name: string;

  constructor(name: string) {
    this.name = name;
  }

  move(distanceInMeters: number = 0) {
    console.log(`${this.name} moved ${distanceInMeters}m.`);
  }
}

class Snake extends Animal {
  constructor(name: string) {
    super(name);
  }

  move(distanceInMeters = 5) {
    console.log("Slithering...");
    super.move(distanceInMeters);
  }
}

let sam = new Snake("Sammy the Python");
sam.move();
```

### 修饰符

```typescript
class Animal {
  public name: string;
  private constructor(theName: string) {
    this.name = theName;
  }
}

// readonly 修饰符
class Octopus {
  readonly name: string;
  readonly numberOfLegs: number = 8;

  constructor(theName: string) {
    this.name = theName;
  }
}

// 存取器
let passcode = "secret passcode";

class Employee {
  private _fullName: string;

  get fullName(): string {
    return this._fullName;
  }

  set fullName(newName: string) {
    if (passcode && passcode == "secret passcode") {
      this._fullName = newName;
    } else {
      console.log("Error: Unauthorized update of employee!");
    }
  }
}

let employee = new Employee();
employee.fullName = "Bob Smith";
if (employee.fullName) {
  alert(employee.fullName);
}
```

### 静态属性

```typescript
class Grid {
  static origin = { x: 0, y: 0 };

  calculateDistanceFromOrigin(point: { x: number; y: number }) {
    let xDist = point.x - Grid.origin.x;
    let yDist = point.y - Grid.origin.y;
    return Math.sqrt(xDist * xDist + yDist * yDist);
  }
}

let grid1 = new Grid();
let grid2 = new Grid();
console.log(grid1.calculateDistanceFromOrigin({ x: 10, y: 10 }));
console.log(Grid.origin); // 静态属性
```

### 抽象类

```typescript
abstract class Animal {
  abstract makeSound(): void;

  move(): void {
    console.log("roaming the earth...");
  }
}

class Cat extends Animal {
  makeSound() {
    console.log("Meow!");
  }
}

let cat = new Cat();
cat.makeSound();
cat.move();
```

## 枚举

### 数字枚举

```typescript
enum Direction {
  Up = 1,
  Down,
  Left,
  Right,
}

enum Direction {
  Up,
  Down,
  Left,
  Right,
}

// 使用
enum UserResponse {
  No = 0,
  Yes = 1,
}

function respond(recipient: string, message: UserResponse): void {
  // ...
}

respond("Princess Caroline", UserResponse.Yes);
```

### 字符串枚举

```typescript
enum Direction {
  Up = "UP",
  Down = "DOWN",
  Left = "LEFT",
  Right = "RIGHT",
}
```

### 计算成员和常量成员

```typescript
enum FileAccess {
  // 常量成员
  None,
  Read = 1 << 1,
  Write = 1 << 2,
  ReadWrite = Read | Write,
  // 计算成员
  G = "123".length,
}
```

### 联合枚举和枚举成员类型

```typescript
enum ShapeKind {
  Circle,
  Square,
}

interface Circle {
  kind: ShapeKind.Circle;
  radius: number;
}

interface Square {
  kind: ShapeKind.Square;
  sideLength: number;
}

let c: Circle = {
  kind: ShapeKind.Circle,
  radius: 100,
};
```

## 类型推断

### 基础类型推断

```typescript
// 变量初始化
let x = 3; // x 被推断为 number

// 函数返回类型
function add(a: number, b: number) {
  return a + b; // 返回类型被推断为 number
}

// 最佳通用类型
let zoo = [new Rhino(), new Elephant(), new Snake()]; // 推断为 Animal[]
```

### 上下文类型

```typescript
// 上下文类型发生在表达式的类型与所处的位置相关时
window.onmousedown = function (mouseEvent) {
  console.log(mouseEvent.button); // mouseEvent 被推断为 MouseEvent
};

// 如果上下文类型表达式包含了明确的类型信息，则会忽略上下文类型
window.onmousedown = function (mouseEvent: any) {
  console.log(mouseEvent.button); // 现在 mouseEvent 是 any 类型
};
```

## 类型兼容性

### 基础规则

```typescript
// 结构化类型系统
interface Named {
  name: string;
}

class Person {
  name: string;
}

let p: Named;
p = new Person(); // OK，因为Person具有name属性

// 函数参数比较
let x = (a: number) => 0;
let y = (b: number, s: string) => 0;

y = x; // OK
x = y; // Error
```

### 枚举类型兼容性

```typescript
enum Status {
  Ready,
  Waiting,
}

enum Color {
  Red,
  Blue,
  Green,
}

let status = Status.Ready;
status = Color.Green; // Error
```

### 类类型兼容性

```typescript
class Animal {
  feet: number;
  constructor(name: string, numFeet: number) {}
}

class Size {
  feet: number;
  constructor(numFeet: number) {}
}

let a: Animal;
let s: Size;

a = s; // OK
s = a; // OK
```

## 高级类型

### 交叉类型

```typescript
interface BusinessPartner {
  name: string;
  credit: number;
}

interface Identity {
  id: number;
  name: string;
}

type Employee = BusinessPartner & Identity;

let e: Employee = {
  id: 100,
  name: "John Doe",
  credit: 7000,
};
```

### 联合类型

```typescript
function padLeft(value: string, padding: string | number) {
  if (typeof padding === "number") {
    return Array(padding + 1).join(" ") + value;
  }
  if (typeof padding === "string") {
    return padding + value;
  }
  throw new Error(`Expected string or number, got '${padding}'.`);
}

// 类型保护
function isNumber(x: any): x is number {
  return typeof x === "number";
}

function isString(x: any): x is string {
  return typeof x === "string";
}

function padLeft(value: string, padding: string | number) {
  if (isNumber(padding)) {
    return Array(padding + 1).join(" ") + value;
  }
  if (isString(padding)) {
    return padding + value;
  }
  throw new Error(`Expected string or number, got '${padding}'.`);
}
```

### 类型别名

```typescript
type Name = string;
type NameResolver = () => string;
type NameOrResolver = Name | NameResolver;

function getName(n: NameOrResolver): Name {
  if (typeof n === "string") {
    return n;
  } else {
    return n();
  }
}

// 泛型类型别名
type Container<T> = { value: T };

// 联合类型别名
type Tree<T> = {
  value: T;
  left: Tree<T>;
  right: Tree<T>;
};
```

### 字面量类型

```typescript
type Easing = "ease-in" | "ease-out" | "ease-in-out";

function UIElement() {
  let width: number | "100%";
  let height: number | "auto";
}

// 可辨识联合
interface Square {
  kind: "square";
  size: number;
}

interface Rectangle {
  kind: "rectangle";
  width: number;
  height: number;
}

interface Circle {
  kind: "circle";
  radius: number;
}

type Shape = Square | Rectangle | Circle;

function area(s: Shape) {
  switch (s.kind) {
    case "square":
      return s.size * s.size;
    case "rectangle":
      return s.width * s.height;
    case "circle":
      return Math.PI * s.radius * s.radius;
  }
}
```

### 索引类型

```typescript
function pluck<T, K extends keyof T>(o: T, names: K[]): T[K][] {
  return names.map(n => o[n]);
}

interface Person {
  name: string;
  age: number;
}

let person: Person = {
  name: "Jarid",
  age: 35,
};

let strings: string[] = pluck(person, ["name"]); // OK, string[]
```

### 映射类型

```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

type PersonPartial = Partial<Person>;
type ReadonlyPerson = Readonly<Person>;

// 条件类型
type NonNullable<T> = T extends null | undefined ? never : T;

// infer 关键字
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;
```

## 装饰器

### 类装饰器

```typescript
function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
class Greeter {
  greeting: string;
  constructor(message: string) {
    this.greeting = message;
  }
  greet() {
    return "Hello, " + this.greeting;
  }
}
```

### 方法装饰器

```typescript
function enumerable(value: boolean) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    descriptor.enumerable = value;
  };
}

class Greeter {
  greeting: string;
  constructor(message: string) {
    this.greeting = message;
  }

  @enumerable(false)
  greet() {
    return "Hello, " + this.greeting;
  }
}
```

### 属性装饰器

```typescript
function format(formatString: string) {
  return function (target: any, key: string): void {
    // property value
    let _val = target[key];

    // property getter
    const getter = function () {
      return `"${formatString}" ${_val}`;
    };

    // property setter
    const setter = function (newVal: string) {
      _val = newVal;
    };

    // Delete property.
    if (delete this[key]) {
      // Create new property with getter and setter
      Object.defineProperty(target, key, {
        get: getter,
        set: setter,
        enumerable: true,
        configurable: true,
      });
    }
  };
}

class Greeter {
  @format("Hello,")
  greeting: string;
}
```

### 参数装饰器

```typescript
function required(target: Object, propertyKey: string | symbol, parameterIndex: number) {
  let requiredParams: number[] = Reflect.getMetadata("required", target, propertyKey) || [];
  requiredParams.push(parameterIndex);
  Reflect.defineMetadata("required", requiredParams, target, propertyKey);
}

class Greeter {
  greeting: string;

  constructor(@required message: string) {
    this.greeting = message;
  }
}
```

## 模块系统

### 导出

```typescript
// 导出声明
export interface StringValidator {
  isAcceptable(s: string): boolean;
}

// 导出语句
export class ZipCodeValidator implements StringValidator {
  isAcceptable(s: string) {
    return s.length === 5 && NumberTest.test(s);
  }
}

// 重新导出
export { ZipCodeValidator };
export { ZipCodeValidator as mainValidator };
export * from "./StringValidator"; // 导出所有
```

### 导入

```typescript
// 导入单个导出
import { ZipCodeValidator } from "./ZipCodeValidator";

// 导入整个模块
import * as validator from "./ZipCodeValidator";

// 具有副作用的导入
import "./my-module.js";

// 默认导出
export default class ZipCodeValidator {
  // ...
}
import ZipCodeValidator from "./ZipCodeValidator";
```

## 声明合并

### 接口合并

```typescript
interface Box {
  height: number;
  width: number;
}

interface Box {
  scale: number;
}

let box: Box = { height: 5, width: 6, scale: 10 };
```

### 命名空间合并

```typescript
namespace Animals {
  export class Zebra {}
}

namespace Animals {
  export interface Legged {
    numberOfLegs: number;
  }
}

// 相当于
namespace Animals {
  export interface Legged {
    numberOfLegs: number;
  }
  export class Zebra {}
}
```

### 命名空间与类合并

```typescript
class Album {
  label: string;
}

namespace Album {
  export class AlbumLabel {}
}

let album: Album = new Album();
album.label = "Classical Hits";
album.AlbumLabel = { name: "Classical Music" };
```

## 实用工具类型

### Partial

```typescript
interface Todo {
  title: string;
  description: string;
}

function updateTodo(todo: Todo, fieldsToUpdate: Partial<Todo>) {
  return { ...todo, ...fieldsToUpdate };
}

const todo1 = {
  title: "organize desk",
  description: "clear clutter",
};

const todo2 = updateTodo(todo1, {
  description: "throw out trash",
});
```

### Required

```typescript
interface Props {
  a?: number;
  b?: string;
}

const obj: Props = { a: 5 };

const obj2: Required<Props> = { a: 5, b: "hello" }; // Error: property 'b' missing
```

### Readonly

```typescript
interface Todo {
  title: string;
}

const todo: Readonly<Todo> = {
  title: "Delete inactive users",
};

todo.title = "Hello"; // Error: cannot reassign a readonly property
```

### Record

```typescript
interface PageInfo {
  title: string;
}

type Page = "home" | "about" | "contact";

const x: Record<Page, PageInfo> = {
  home: { title: "Home" },
  about: { title: "About" },
  contact: { title: "Contact" },
};
```

### Pick

```typescript
interface Todo {
  title: string;
  description: string;
  completed: boolean;
}

type TodoPreview = Pick<Todo, "title" | "completed">;

const todo: TodoPreview = {
  title: "Clean room",
  completed: false,
};
```

### Omit

```typescript
interface Todo {
  title: string;
  description: string;
  completed: boolean;
  createdAt: number;
}

type TodoPreview = Omit<Todo, "description">;

const todo: TodoPreview = {
  title: "Clean room",
  completed: false,
  createdAt: 1615544252770,
};
```

### Exclude

```typescript
type T0 = Exclude<"a" | "b" | "c", "a">; // "b" | "c"
type T1 = Exclude<string | number | (() => void), Function>; // string | number
```

### Extract

```typescript
type T0 = Extract<"a" | "b" | "c", "a" | "f">; // "a"
type T1 = Extract<string | number | (() => void), Function>; // () => void
```

### NonNullable

```typescript
type T0 = NonNullable<string | number | undefined>; // string | number
type T1 = NonNullable<string[] | null | undefined>; // string[]
```

### ReturnType

```typescript
declare function f1(): { a: number; b: string };

type T0 = ReturnType<() => string>; // string
type T1 = ReturnType<() => Promise<number>>; // Promise<number>
type T2 = ReturnType<typeof f1>; // { a: number, b: string }
```

### InstanceType

```typescript
class C {
  x = 0;
  y = 0;
}

type T0 = InstanceType<typeof C>; // C
type T1 = InstanceType<() => string>; // Error
```

## 常用模式

### 单例模式

```typescript
class Singleton {
  private static instance: Singleton;

  private constructor() {}

  public static getInstance(): Singleton {
    if (!Singleton.instance) {
      Singleton.instance = new Singleton();
    }
    return Singleton.instance;
  }

  public someBusinessLogic() {
    // ...
  }
}

const singleton1 = Singleton.getInstance();
const singleton2 = Singleton.getInstance();
console.log(singleton1 === singleton2); // true
```

### 工厂模式

```typescript
interface Product {
  operation(): string;
}

class ConcreteProduct1 implements Product {
  public operation(): string {
    return "{Result of ConcreteProduct1}";
  }
}

class ConcreteProduct2 implements Product {
  public operation(): string {
    return "{Result of ConcreteProduct2}";
  }
}

abstract class Creator {
  public abstract factoryMethod(): Product;

  public someOperation(): string {
    const product = this.factoryMethod();
    return `Creator: The same creator's code has just worked with ${product.operation()}`;
  }
}

class ConcreteCreator1 extends Creator {
  public factoryMethod(): Product {
    return new ConcreteProduct1();
  }
}

class ConcreteCreator2 extends Creator {
  public factoryMethod(): Product {
    return new ConcreteProduct2();
  }
}

function clientCode(creator: Creator) {
  console.log(creator.someOperation());
}

clientCode(new ConcreteCreator1());
clientCode(new ConcreteCreator2());
```

### 观察者模式

```typescript
interface Observer {
  update(subject: Subject): void;
}

interface Subject {
  attach(observer: Observer): void;
  detach(observer: Observer): void;
  notify(): void;
}

class ConcreteSubject implements Subject {
  public state: number = 0;
  private observers: Observer[] = [];

  public attach(observer: Observer): void {
    const isExist = this.observers.includes(observer);
    if (isExist) {
      return console.log("Subject: Observer has been attached already.");
    }

    console.log("Subject: Attached an observer.");
    this.observers.push(observer);
  }

  public detach(observer: Observer): void {
    const observerIndex = this.observers.indexOf(observer);
    if (observerIndex === -1) {
      return console.log("Subject: Nonexistent observer.");
    }

    this.observers.splice(observerIndex, 1);
    console.log("Subject: Detached an observer.");
  }

  public notify(): void {
    console.log("Subject: Notifying observers...");
    for (const observer of this.observers) {
      observer.update(this);
    }
  }

  public someBusinessLogic(): void {
    console.log("\nSubject: I'm doing something important.");
    this.state = Math.floor(Math.random() * (10 + 1));

    console.log(`Subject: My state has just changed to: ${this.state}`);
    this.notify();
  }
}

class ConcreteObserverA implements Observer {
  public update(subject: Subject): void {
    if (subject instanceof ConcreteSubject && subject.state < 3) {
      console.log("ConcreteObserverA: Reacted to the event.");
    }
  }
}

class ConcreteObserverB implements Observer {
  public update(subject: Subject): void {
    if (subject instanceof ConcreteSubject && (subject.state === 0 || subject.state >= 2)) {
      console.log("ConcreteObserverB: Reacted to the event.");
    }
  }
}

const subject = new ConcreteSubject();

const observer1 = new ConcreteObserverA();
subject.attach(observer1);

const observer2 = new ConcreteObserverB();
subject.attach(observer2);

subject.someBusinessLogic();
subject.someBusinessLogic();

subject.detach(observer1);
subject.someBusinessLogic();
```

### 策略模式

```typescript
interface Strategy {
  doAlgorithm(data: number[]): number[];
}

class ConcreteStrategyA implements Strategy {
  public doAlgorithm(data: number[]): number[] {
    return data.sort();
  }
}

class ConcreteStrategyB implements Strategy {
  public doAlgorithm(data: number[]): number[] {
    return data.reverse();
  }
}

class Context {
  private strategy: Strategy;

  constructor(strategy: Strategy) {
    this.strategy = strategy;
  }

  public setStrategy(strategy: Strategy): void {
    this.strategy = strategy;
  }

  public doSomeBusinessLogic(): void {
    const result = this.strategy.doAlgorithm([1, 2, 3]);
    console.log(result.join(","));
  }
}

const context = new Context(new ConcreteStrategyA());
console.log("Client: Strategy is set to normal sorting.");
context.doSomeBusinessLogic();

console.log("Client: Strategy is set to reverse sorting.");
context.setStrategy(new ConcreteStrategyB());
context.doSomeBusinessLogic();
```

这个速查手册涵盖了 TypeScript 开发中最常用的概念和模式，可以作为日常开发的参考指南。对于从 PHP 转向 TypeScript 的开发者，重点关注类型系统、接口、泛型和模块系统的部分。