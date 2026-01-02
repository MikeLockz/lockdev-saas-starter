import * as ts from "typescript";
import { Primitive } from "../utils";
import { TypeDefinition, TypeDefinitionObject, TypeReferenceLike } from ".";
export declare function isTypeReferenceLike(value: unknown): value is TypeReferenceLike;
export declare function isTypeDefinitionObject(object: unknown): object is TypeDefinitionObject;
export declare function isTypeDefinition(value: unknown): value is TypeDefinition;
export declare function toTypeNode(definition: TypeDefinition): ts.TypeNode;
/**
 * Create a property signature, this is primarily used
 * internally and does not have much usage outside of that.
 *
 * @param name The property name.
 * @param definition The type definition.
 */
export declare function typeProperty(name: string, definition: TypeDefinition): ts.PropertySignature;
/**
 * Create a literal type, this is primarily used
 * internally and does not have much usage outside of that.
 *
 * @param definition A primitive, like a number or a boolean.
 */
export declare function typeLiteral(definition: Primitive): ts.LiteralTypeNode;
/**
 * Create a type literal, this is primarily used
 * internally and does not have much usage outside of that.
 *
 * @param definition A object type definition.
 */
export declare function typeLiteral(definition: TypeDefinitionObject): ts.TypeLiteralNode;
export declare function typeLiteral(definition: TypeDefinitionObject | Primitive): ts.LiteralTypeNode | ts.TypeLiteralNode;
