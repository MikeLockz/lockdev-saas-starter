import { Get } from "type-fest";
import type { HasNestedPath, ObjectLiteral } from "../typings";
/** Sets a nested property value from a dot-delimited path */
export declare function set<Value = any, From = ObjectLiteral>(obj: From, path: string, value: Value): void;
/** Sets a nested property value using a getter that points to the parent prop on which the value will be set */
export declare function set<Value = any, From = ObjectLiteral>(obj: From, getter: (value: From) => any, prop: string, value: Value): void;
export declare const makeGetter: <Path extends string>(path: Path) => HasNestedPath<Path> extends 1 ? <From extends ObjectLiteral<any>, Return = From[Path]>(obj: From) => Return : <From_1 extends ObjectLiteral<any>, Return_1 = import("type-fest/source/get").GetWithPath<From_1, Path extends string ? import("type-fest").Split<import("type-fest/source/get").FixPathSquareBrackets<Path>, "."> : Path, {}>>(obj: From_1) => Return_1;
/** Get a nested property value from a dot-delimited path. */
export declare function get<Path extends string, From extends ObjectLiteral, Return = HasNestedPath<Path> extends 1 ? From[Path] : Get<From, Path>>(obj: From, path: Path): Return;
/** Remove key at path in an object */
export declare function remove<From = ObjectLiteral>(obj: From, path: string): void;
type TUnionToIntersection<U> = (U extends any ? (k: U) => void : never) extends (k: infer I) => void ? I : never;
/** Deep merge arrays from left into right, can use unique array values for merged properties */
export declare function deepMerge<T extends ObjectLiteral[]>(inputs: Partial<T>, options?: DeepMergeOptions): TUnionToIntersection<T[number]>;
export type DeepMergeOptions = {
    withUniqueArrayValues?: boolean;
};
export type ComparatorFn = (a: string, b: string) => number;
/** Deeply sort an object's properties using given sort function */
export declare function deepSort<T>(src: T, comparator?: ComparatorFn): T;
export {};
//# sourceMappingURL=nested.d.ts.map