"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.var = exports.let = exports.const = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("./utils");
function variableStatement(name, definition, options) {
    const node = (0, utils_1.toRuntimeNode)(definition);
    return ts.factory.createVariableStatement([ts.factory.createModifier(ts.SyntaxKind.ExportKeyword)], ts.factory.createVariableDeclarationList([ts.factory.createVariableDeclaration(name, undefined, options.type, node)], {
        const: ts.NodeFlags.Const,
        let: ts.NodeFlags.Let,
        var: ts.NodeFlags.None
    }[options.kind]));
}
function const_(name, definition, options = {}) {
    return variableStatement(name, definition, Object.assign(Object.assign({}, options), { kind: "const" }));
}
exports.const = const_;
function let_(name, definition, options = {}) {
    return variableStatement(name, definition, Object.assign(Object.assign({}, options), { kind: "let" }));
}
exports.let = let_;
function var_(name, definition, options = {}) {
    return variableStatement(name, definition, Object.assign(Object.assign({}, options), { kind: "var" }));
}
exports.var = var_;
