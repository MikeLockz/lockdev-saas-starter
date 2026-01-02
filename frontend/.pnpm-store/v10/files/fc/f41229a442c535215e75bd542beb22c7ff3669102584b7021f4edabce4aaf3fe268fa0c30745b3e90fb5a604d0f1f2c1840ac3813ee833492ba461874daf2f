import * as ts from "typescript";
import { RuntimeDefinition } from "./runtime";
import { TypeDefinition } from "./type";
export declare type AnyDefinition = RuntimeDefinition | TypeDefinition;
/**
 * Create a single line comment.
 *
 * @param definition The type definition.
 * @param comment The single line comment.
 */
export declare function comment<T extends AnyDefinition>(definition: T, comment: string): T extends TypeDefinition ? ts.TypeNode : ts.Node;
/**
 * Create comment spanning multiple lines.
 *
 * @param definition The type definition.
 * @param comment An array of strings, constituting a multiline comment.
 */
export declare function comment<T>(definition: T, comment: Array<string>): T extends TypeDefinition ? ts.TypeNode : ts.Node;
