import * as ts from "typescript";
export declare type Primitive = string | number | boolean | bigint;
export declare const PrimitiveTypes: readonly ["string", "number", "boolean", "bigint"];
export declare type PrimitiveTypes = typeof PrimitiveTypes[number];
export declare function isPrimitive(value: unknown): value is Primitive;
export declare function isNode(value: unknown): value is ts.Node;
export declare function setLazy<T extends object>(defaultValue: T, immediateValue: () => T): T;
