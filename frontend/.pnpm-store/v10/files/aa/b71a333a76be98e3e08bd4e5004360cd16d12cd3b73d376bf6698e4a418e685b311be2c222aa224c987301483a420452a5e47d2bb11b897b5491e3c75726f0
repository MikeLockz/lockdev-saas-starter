import * as ts from "typescript";
import { Primitive } from "../utils";
import { RuntimeDefinition, RuntimeDefinitionObject, ReferenceLike } from ".";
export declare type BooleanRuntimeLiteral = ts.TrueLiteral | ts.FalseLiteral;
export declare type PrimitiveRuntimeLiteral = ts.StringLiteral | ts.NumericLiteral | BooleanRuntimeLiteral | ts.BigIntLiteral;
export declare function isReferenceLike(value: unknown): value is ReferenceLike;
export declare function isRuntimeDefinitionObject(object: unknown): object is RuntimeDefinitionObject;
export declare function isRuntimeDefinition(value: unknown): value is RuntimeDefinition;
export declare function toRuntimeNode(definition: RuntimeDefinition, reference?: boolean): ts.Node;
export declare function runtimeReference(definition: ReferenceLike): ts.Identifier;
/**
 * Create a property signature, this is primarily used
 * internally and does not have much usage outside of that.
 *
 * @param name The property name.
 * @param definition The type definition.
 */
export declare function runtimeProperty(name: string, definition: RuntimeDefinition): ts.PropertyAssignment;
/**
 * Create a literal type, this is primarily used
 * internally and does not have much usage outside of that.
 *
 * @param definition A primitive, like a number or a boolean.
 */
export declare function runtimeLiteral(definition: string): ts.StringLiteral;
export declare function runtimeLiteral(definition: number): ts.NumericLiteral;
export declare function runtimeLiteral(definition: boolean): BooleanRuntimeLiteral;
export declare function runtimeLiteral(definition: Primitive): PrimitiveRuntimeLiteral;
export declare function runtimeLiteral(definition: RuntimeDefinitionObject): ts.ObjectLiteralExpression;
export declare function runtimeLiteral(definition: RuntimeDefinitionObject | Primitive): PrimitiveRuntimeLiteral | ts.ObjectLiteralExpression;
