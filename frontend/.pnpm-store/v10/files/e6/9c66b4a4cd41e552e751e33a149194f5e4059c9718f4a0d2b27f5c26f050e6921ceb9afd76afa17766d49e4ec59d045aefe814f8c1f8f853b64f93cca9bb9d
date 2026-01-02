import { CType, NonFunctionKeys, ObjectLiteral } from "../typings";
/** Map an object to another using given schema, can use a dot delimited path for mapping to nested properties */
export declare const mapper: <Schema = ObjectLiteral<any>, Values = ObjectLiteral<any>>(schema: Schema, obj: Values) => ObjectLiteral<any>;
/** Reverse an object from its schema */
export declare const reverse: <Schema = ObjectLiteral<any>>(schema: Schema) => {};
/** Make an instance of given class auto-filled with record values */
export declare const makeInstance: <Instance extends object>(instance: CType<Instance>, record: Partial<{ [Key in NonFunctionKeys<Instance>]: Instance[Key]; }>) => Instance;
/** Polyfill Object.fromEntries */
export declare function fromEntries<K extends string, V>(iterable: Iterable<readonly [K, V]> | Array<[K, V]>): Record<K, V>;
/** Sort object keys alphabetically */
export declare const sortObjectKeys: <T = ObjectLiteral<any>>(obj: T) => T;
/** Sort object keys using a reference order array, sort keys not in reference order in lasts positions */
export declare const sortObjKeysFromArray: <T = ObjectLiteral<any>>(obj: T, orderedKeys: (keyof T)[]) => {
    [k: string]: T[keyof T];
};
/**
 * Hashes the value into a stable hash.
 * @see Adapted from https://github.com/tannerlinsley/react-query/blob/e42cbc32dfcd9add24cadd06135e42af1dbbc8ad/src/core/utils.ts
 */
export declare function hash<T extends ObjectLiteral = ObjectLiteral>(value: T): string;
export declare function groupBy<Key extends keyof T, T extends ObjectLiteral>(array: T[], keyOrGetter: Key): Record<T[Key], T[]>;
export declare function groupBy<T, KeyReturnT>(array: T[], keyOrGetter: (item: T) => KeyReturnT): KeyReturnT extends string | number ? Record<KeyReturnT, T[]> : never;
export declare function groupIn<Key extends keyof T, T extends ObjectLiteral>(array: T[], keyOrGetter: Key): Record<T[Key], T>;
export declare function groupIn<T, KeyReturnT>(array: T[], keyOrGetter: (item: T) => KeyReturnT): KeyReturnT extends string | number ? Record<KeyReturnT, T> : never;
export declare const mergeProps: <Left extends ObjectLiteral<any>, Right extends Partial<Left & {}>>(left: Left, right: Right) => Left & Right;
export declare function keys<T extends object>(value: T): Array<keyof T & string>;
//# sourceMappingURL=object.d.ts.map