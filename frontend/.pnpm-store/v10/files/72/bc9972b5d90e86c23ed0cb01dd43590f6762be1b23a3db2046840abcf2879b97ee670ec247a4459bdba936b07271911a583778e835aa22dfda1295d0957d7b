import * as ts from "typescript";
export interface GenerateOptions {
    banner?: string;
}
/**
 * Generate the file source as a string.
 * @param nodes An array of nodes.
 */
export declare function generate(nodes: Array<ts.Node>, options?: GenerateOptions): Promise<string>;
export declare function generateFile(path: string, nodes: Array<ts.Node>, options?: GenerateOptions): Promise<void>;
