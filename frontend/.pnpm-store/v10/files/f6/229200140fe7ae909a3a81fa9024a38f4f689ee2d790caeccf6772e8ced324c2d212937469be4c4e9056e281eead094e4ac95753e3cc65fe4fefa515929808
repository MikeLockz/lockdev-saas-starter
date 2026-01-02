"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.never = exports.void = exports.undefined = exports.unknown = exports.any = exports.date = exports.boolean = exports.bigint = exports.number = exports.string = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const __1 = require("..");
/**
 * Create a string primitive.
 */
function string() {
    return ts.factory.createKeywordTypeNode(ts.SyntaxKind.StringKeyword);
}
exports.string = string;
/**
 * Create a number primitive.
 */
function number() {
    return ts.factory.createKeywordTypeNode(ts.SyntaxKind.NumberKeyword);
}
exports.number = number;
/**
 * Create a bigint primitive.
 * @see [BigInt on MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt)
 */
function bigint() {
    return ts.factory.createKeywordTypeNode(ts.SyntaxKind.BigIntKeyword);
}
exports.bigint = bigint;
/**
 * Create a boolean primitive.
 */
function boolean() {
    return ts.factory.createKeywordTypeNode(ts.SyntaxKind.BooleanKeyword);
}
exports.boolean = boolean;
/**
 * Shorthand for a reference to the Date class,
 * this is equivalent to ``t.reference("Date")``.
 */
function date() {
    return (0, __1.reference)("Date");
}
exports.date = date;
function any() {
    return ts.factory.createKeywordTypeNode(ts.SyntaxKind.AnyKeyword);
}
exports.any = any;
function unknown() {
    return ts.factory.createKeywordTypeNode(ts.SyntaxKind.UnknownKeyword);
}
exports.unknown = unknown;
function undefined_() {
    return ts.factory.createKeywordTypeNode(ts.SyntaxKind.UndefinedKeyword);
}
exports.undefined = undefined_;
function void_() {
    return ts.factory.createKeywordTypeNode(ts.SyntaxKind.VoidKeyword);
}
exports.void = void_;
function never() {
    return ts.factory.createKeywordTypeNode(ts.SyntaxKind.NeverKeyword);
}
exports.never = never;
