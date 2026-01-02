import * as ts from "typescript";
import { TypeDefinition } from "..";
/**
 * Create an tuple from array of type definitions.
 * A tuple is a special-cased array with known types at specific indexes.
 *
 * @param definitions An array of type definitions.
 */
export declare function tuple(definitions: Array<TypeDefinition>): ts.TupleTypeNode;
/**
 * Create a named tuple from an definition object.
 * @param definitions An object, with the property keys used as the tuple entry name.
 */
export declare function tuple(definitions: Record<string, TypeDefinition>): ts.TupleTypeNode;
