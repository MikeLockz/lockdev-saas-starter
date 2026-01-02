import { ObjectLiteral } from "../typings";
/** Pick given properties in object */
export declare function pick<T, K extends keyof T>(obj: T, paths: K[]): Pick<T, K>;
/** Creates an object composed of the picked object properties that satisfies the condition for each value */
export declare function pickBy<T, K extends keyof T>(obj: T, paths: K[], fn: (key: keyof T, value: T[keyof T]) => boolean): Partial<Pick<T, K>>;
/** Only pick given properties that are defined in object */
export declare const pickDefined: <T, K extends keyof T>(obj: T, paths: K[]) => Partial<Pick<T, K>>;
/** Omit given properties from object */
export declare function omit<T extends ObjectLiteral, K extends keyof T>(object: T, keys: K[]): Omit<T, K>;
export type Formater<Value = any, Return = any, Key extends any = string> = (value: Value, key: Key) => Return;
/** Format object values using a given method */
export declare const format: <Return = ObjectLiteral<any>, Method extends Function = Formater<any, any, string>, From = ObjectLiteral<any>>(obj: From, method?: Method) => Return;
/** Remove undefined properties in object */
export declare const removeUndefineds: <Value = ObjectLiteral<any>>(obj: Value) => {};
/**
 * Returns true if a value differs between a & b, only check for the first level (shallow)
 * @see https://github.com/preactjs/preact-compat/blob/7c5de00e7c85e2ffd011bf3af02899b63f699d3a/src/index.js#L349
 */
export declare function hasShallowDiff(a: Record<any, any>, b: Record<any, any>): boolean;
/** Returns keys that are both in a & b */
export declare function getCommonKeys(abc: ObjectLiteral, xyz: ObjectLiteral): string[];
/** Returns true if a value differs between a & b in their common properties */
export declare function hasShallowDiffInCommonKeys(abc: ObjectLiteral, xyz: ObjectLiteral): boolean;
//# sourceMappingURL=pick.d.ts.map