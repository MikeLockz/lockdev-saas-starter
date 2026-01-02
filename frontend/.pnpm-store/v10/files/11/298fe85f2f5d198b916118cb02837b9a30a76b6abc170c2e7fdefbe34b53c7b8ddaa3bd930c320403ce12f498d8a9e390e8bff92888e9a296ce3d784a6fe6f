"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const tslib_1 = require("tslib");
const _1 = require("./");
/**
 * A quick demonstration of converting a
 * JSON object to a TypeScript interface.
 */
function toTypeScript(name, rootObject) {
    function recursive(object) {
        return Object.fromEntries(Object.entries(object).map(([key, value]) => {
            if (typeof value === "object")
                return [key, recursive(value)];
            const kind = typeof value === "string"
                ? _1.t.string()
                : typeof value === "number"
                    ? _1.t.number()
                    : typeof value === "boolean"
                        ? _1.t.boolean
                        : _1.t.undefined();
            return [key, kind];
        }));
    }
    return _1.t.interface(name, recursive(rootObject));
}
void (() => tslib_1.__awaiter(void 0, void 0, void 0, function* () {
    /**
     * Create an interface from a json object. This isn't technically
     * part of the exposed api, but it's good for demonstration purposes.
     */
    const User = toTypeScript("User", {
        id: 1,
        name: "Leanne Graham",
        username: "Bret",
        emails: ["sincere@april.biz", "leanne.graham@gajin.sh"],
        address: {
            street: "Kulas Light",
            suite: "Apt. 556",
            city: "Gwenborough",
            zipcode: "92998-3874",
            geo: {
                lat: "-37.3159",
                lng: "81.1496"
            }
        },
        phone: "1-770-736-8031 x56442",
        website: "hildegard.org",
        company: {
            name: "Romaguera-Crona",
            catchPhrase: "Multi-layered client-server neural-net",
            bs: "harness real-time e-markets"
        }
    });
    const MemberRole = _1.t.enum("MemberRole", ["DEFAULT", "SPONSOR", "ADMINISTRATOR"]);
    const Member = _1.t.interface("Member", {
        user: User,
        role: MemberRole
    });
    const Foo = _1.t.type("Foo", _1.t.intersection([1, 2]));
    const Organization = _1.t.interface("Organization", {
        id: _1.t.readonly(_1.t.number()),
        name: _1.t.comment(_1.t.string(), [
            "The organization name",
            "@see https://example.com/organization-name"
        ]),
        description: _1.t.optional(_1.t.string()),
        members: _1.t.array(Member)
    });
    const a = _1.t.const("a", _1.t.propertyOf(MemberRole, "DEFAULT"));
    const b = _1.t.const("b", _1.t.as({
        foo: {
            "bar/baz": true
        }
    }, "const"));
    const B = _1.t.type("B", _1.t.indexOf(_1.t.typeof(b), "foo"));
    const RecursiveInterface = _1.t.interface("RecursiveInterface", () => ({
        foo: RecursiveInterface
    }));
    yield _1.t.generateFile("./src/example.out.ts", [
        User,
        MemberRole,
        Member,
        Organization,
        Foo,
        a,
        b,
        B,
        RecursiveInterface
    ]);
}))();
