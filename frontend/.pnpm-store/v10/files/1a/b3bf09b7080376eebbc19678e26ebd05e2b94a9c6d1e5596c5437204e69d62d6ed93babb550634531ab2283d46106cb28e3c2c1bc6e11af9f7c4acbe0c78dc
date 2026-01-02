export interface User {
    id: number;
    name: string;
    username: string;
    emails: {
        0: string;
        1: string;
    };
    address: {
        street: string;
        suite: string;
        city: string;
        zipcode: string;
        geo: {
            lat: string;
            lng: string;
        };
    };
    phone: string;
    website: string;
    company: {
        name: string;
        catchPhrase: string;
        bs: string;
    };
}
export declare enum MemberRole {
    DEFAULT = 0,
    SPONSOR = 1,
    ADMINISTRATOR = 2
}
export interface Member {
    user: User;
    role: MemberRole;
}
export interface Organization {
    readonly id: Readonly<number>;
    /**
     * The organization name
     * @see https://example.com/organization-name
     */
    name: string;
    description?: string | undefined;
    members: Array<Member>;
}
export declare type Foo = 1 & 2;
declare const b: {
    readonly foo: {
        readonly "bar/baz": true;
    };
};
export declare type B = (typeof b)["foo"];
export interface RecursiveInterface {
    foo: RecursiveInterface;
}
export {};
