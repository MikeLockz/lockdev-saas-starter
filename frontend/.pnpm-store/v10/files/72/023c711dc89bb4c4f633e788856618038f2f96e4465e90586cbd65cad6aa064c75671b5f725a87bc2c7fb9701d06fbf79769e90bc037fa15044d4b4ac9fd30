import * as ts from "typescript";
import { ReferenceLike } from "../runtime";
import { Primitive } from "../utils";
export * from "./composites";
export * from "./declarations";
export * from "./modifiers";
export * from "./primitives";
/**
 * A value that can be referenced within
 * the scope of a type definition.
 */
export declare type TypeReferenceLike = ts.TypeNode | ts.TypeAliasDeclaration | ts.InterfaceDeclaration | ts.EnumDeclaration;
/**
 * An object, with type definitions as values.
 */
export interface TypeDefinitionObject {
    [K: string]: TypeDefinition;
}
export declare type TypeDefinition = TypeReferenceLike | TypeDefinitionObject | Primitive;
/**
 * Create a reference to another type, this is primarily used
 * internally but can be used to refer to types that aren't within scope.
 *
 * @param node A string to create a artificial reference of.
 * @param typeArguments The generic parameters to pass to the referenced type.
 */
export declare function reference(node: string, typeArguments?: Array<TypeDefinition>): ts.TypeNode;
/**
 * Create a reference to another type, this is primarily used
 * internally but can be used to refer to types that aren't within scope.
 *
 * @param node A node that can be referenced.
 * @param typeArguments The generic parameters to pass to the referenced type.
 */
export declare function reference(node: TypeReferenceLike, typeArguments?: Array<TypeDefinition>): ts.TypeNode;
/**
 * Create an array type from a type definition.
 * @param definition The type definition.
 */
export declare function array(definition: TypeDefinition): ts.TypeReferenceNode;
/**
 * "typeof" is a reserved keyword.
 */
export { typeof_ as typeof };
declare function typeof_(value: ReferenceLike): ts.TypeQueryNode;
export declare function indexOf(definition: TypeDefinition, index: string | number): ts.IndexedAccessTypeNode;
