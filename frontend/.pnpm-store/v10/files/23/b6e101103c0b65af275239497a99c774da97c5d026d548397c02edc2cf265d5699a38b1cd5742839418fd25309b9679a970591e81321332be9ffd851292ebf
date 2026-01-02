import * as ts from "typescript";
import { TypeDefinitionObject } from "..";
/**
 * "interface" is a reserved keyword.
 */
export { interface_ as interface };
/**
 * Create an interface. Used to describe the shape
 * of objects, and can be extended by others.
 *
 * @param name The name of the interface.
 * @param properties An object, with type definitions as values or a function which lazily returns them.
 */
declare function interface_(name: string, properties: TypeDefinitionObject | (() => TypeDefinitionObject)): ts.InterfaceDeclaration;
