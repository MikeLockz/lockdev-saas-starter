import * as ts from "typescript";
export interface ModuleOptions {
    declare?: boolean;
    namespace?: boolean;
    global?: boolean;
}
export declare function module(name: string, statements: Array<ts.InterfaceDeclaration | ts.ModuleDeclaration>, options?: ModuleOptions): ts.ModuleDeclaration;
/**
 * Shorthand for creating a module namespace, this is equivalent to
 * ``t.module(name, statements, { ...options, namespace: true })``.
 */
export declare function namespace(name: string, statements: Array<ts.InterfaceDeclaration | ts.ModuleDeclaration>, options?: ModuleOptions): ts.ModuleDeclaration;
