"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.namespace = exports.module = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
function module(name, statements, options = {}) {
    let flags = ts.NodeFlags.None;
    if (name === "global" || options.global)
        flags |= ts.NodeFlags.GlobalAugmentation;
    if (options.namespace)
        flags |= ts.NodeFlags.Namespace;
    return ts.factory.createModuleDeclaration(undefined, options.declare ? [ts.factory.createModifier(ts.SyntaxKind.DeclareKeyword)] : undefined, ts.factory.createIdentifier(name), ts.factory.createModuleBlock(statements), flags);
}
exports.module = module;
/**
 * Shorthand for creating a module namespace, this is equivalent to
 * ``t.module(name, statements, { ...options, namespace: true })``.
 */
function namespace(name, statements, options = {}) {
    return module(name, statements, Object.assign(Object.assign({}, options), { namespace: true }));
}
exports.namespace = namespace;
