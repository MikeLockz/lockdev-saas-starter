import { CType, ObjectLiteral, PrimitiveValue } from "../typings";
export declare const isDefined: <T = any>(value: T) => value is T extends undefined ? never : T extends null ? never : T;
type Nullable<T> = T | null | undefined;
export declare const isNotNullish: <T>(element: T) => element is T;
/** Returns true if value is a string|number|boolean */
export declare const isPrimitive: (value: any) => value is PrimitiveValue;
/** Returns true if typeof value is object && not null */
export declare const isObject: (value: any) => value is object;
/** Returns true if value extends basic Object prototype and is not a Date */
export declare const isObjectLiteral: <T>(value: any) => value is T extends unknown ? ObjectLiteral<any> : T;
export declare const isDate: (value: any) => value is Date;
export declare const isPromise: <T = any>(p: any) => p is Promise<T>;
/** Can be used as type guard  */
export declare const isType: <T>(_value: any, condition?: boolean) => _value is T;
export declare const isClassRegex: RegExp;
export declare const isClass: <T>(value: any) => value is CType<T>;
export declare const isServer: () => boolean;
export declare const isBrowser: () => boolean;
export {};
//# sourceMappingURL=asserts.d.ts.map