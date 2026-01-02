"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.typeLiteral = exports.typeProperty = exports.toTypeNode = exports.isTypeDefinition = exports.isTypeDefinitionObject = exports.isTypeReferenceLike = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("../utils");
const utils_2 = require("../runtime/utils");
const _1 = require(".");
function isTypeReferenceLike(value) {
    return ((0, utils_1.isNode)(value) &&
        (ts.isTypeNode(value) ||
            ts.isTypeAliasDeclaration(value) ||
            ts.isInterfaceDeclaration(value) ||
            ts.isEnumDeclaration(value)));
}
exports.isTypeReferenceLike = isTypeReferenceLike;
function isTypeDefinitionObject(object) {
    if (typeof object !== "object" || !object)
        return false;
    for (const value of Object.values(object)) {
        if (!isTypeDefinition(value))
            return false;
    }
    return true;
}
exports.isTypeDefinitionObject = isTypeDefinitionObject;
function isTypeDefinition(value) {
    return isTypeReferenceLike(value) || isTypeDefinitionObject(value) || (0, utils_1.isPrimitive)(value);
}
exports.isTypeDefinition = isTypeDefinition;
function toTypeNode(definition) {
    return isTypeReferenceLike(definition) ? (0, _1.reference)(definition) : typeLiteral(definition);
}
exports.toTypeNode = toTypeNode;
/**
 * Create a property signature, this is primarily used
 * internally and does not have much usage outside of that.
 *
 * @param name The property name.
 * @param definition The type definition.
 */
function typeProperty(name, definition) {
    var _a;
    const node = toTypeNode(definition);
    const optional = ts.isUnionTypeNode(node)
        ? node.types.find((value) => value.kind === ts.SyntaxKind.UndefinedKeyword) &&
            ts.factory.createToken(ts.SyntaxKind.QuestionToken)
        : undefined;
    const modifiers = [];
    if (ts.isTypeReferenceNode(node) &&
        ts.isIdentifier(node.typeName) &&
        node.typeName.escapedText === "Readonly")
        modifiers.push(ts.factory.createToken(ts.SyntaxKind.ReadonlyKeyword));
    const propertyComments = (_a = ts.getSyntheticLeadingComments(node)) !== null && _a !== void 0 ? _a : [];
    if (propertyComments.length !== 0)
        ts.setSyntheticLeadingComments(node, []);
    const tsPropertySignature = ts.factory.createPropertySignature(modifiers.length ? modifiers : undefined, name, optional, node);
    return propertyComments.length !== 0
        ? ts.setSyntheticLeadingComments(tsPropertySignature, propertyComments)
        : tsPropertySignature;
}
exports.typeProperty = typeProperty;
function typeLiteral(definition) {
    if ((0, utils_1.isPrimitive)(definition))
        return ts.factory.createLiteralTypeNode((0, utils_2.runtimeLiteral)(definition));
    return ts.factory.createTypeLiteralNode(Object.entries(definition).map(([key, node]) => {
        return typeProperty(key, node);
    }));
}
exports.typeLiteral = typeLiteral;
