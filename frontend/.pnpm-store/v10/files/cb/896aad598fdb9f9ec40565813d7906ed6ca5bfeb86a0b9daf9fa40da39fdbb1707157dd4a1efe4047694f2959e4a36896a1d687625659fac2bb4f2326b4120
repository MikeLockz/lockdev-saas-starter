import * as ts from "typescript";
import { RuntimeDefinition } from ".";
export declare type VariableStatementKind = "const" | "let" | "var";
export interface VariableStatementOptions {
    type?: ts.TypeNode;
    kind: VariableStatementKind;
}
/**
 * "const" is a reserved keyword.
 */
export { const_ as const };
declare function const_(name: string, definition: RuntimeDefinition, options?: Omit<VariableStatementOptions, "kind">): ts.VariableStatement;
/**
 * "let" is a reserved keyword.
 */
export { let_ as let };
declare function let_(name: string, definition: RuntimeDefinition, options?: Omit<VariableStatementOptions, "kind">): ts.VariableStatement;
/**
 * "var" is a reserved keyword.
 */
export { var_ as var };
declare function var_(name: string, definition: RuntimeDefinition, options?: Omit<VariableStatementOptions, "kind">): ts.VariableStatement;
