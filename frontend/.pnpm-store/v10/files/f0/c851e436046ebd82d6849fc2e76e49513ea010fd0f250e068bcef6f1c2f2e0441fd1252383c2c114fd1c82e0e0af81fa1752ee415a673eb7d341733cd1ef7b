import * as ts from "typescript";
import { TypeDefinition } from "../type";
import { Primitive } from "../utils";
export declare type ReferenceLike = ts.EnumDeclaration | ts.VariableStatement;
export interface RuntimeDefinitionObject {
    [K: string]: RuntimeDefinition;
}
export declare type RuntimeDefinition = ReferenceLike | RuntimeDefinitionObject | Primitive | ts.Node;
export * from "./statements";
export declare function propertyOf(definition: RuntimeDefinition, key: string): ts.PropertyAccessExpression;
export declare function propertyOf(definition: RuntimeDefinition, key: number): ts.ElementAccessExpression;
export declare function as(definition: RuntimeDefinition, type: (TypeDefinition & {}) | "const"): ts.AsExpression;
