import React from 'react';

/**
 * RoleGuard conditionally renders children based on the user's role.
 * @param {Object} props
 * @param {string|string[]} props.roles - Allowed role(s)
 * @param {Object} props.user - The current user object
 * @param {React.ReactNode} props.children
 * @param {React.ReactNode} [props.fallback=null] - Optional fallback UI
 */
const RoleGuard = ({ roles, user, children, fallback = null }) => {
    if (!user || !user.role_name) return fallback;

    const allowedRoles = Array.isArray(roles) ? roles : [roles];
    const isAllowed = allowedRoles.includes(user.role_name) || user.role_name === 'IssuerAdmin';

    return isAllowed ? children : fallback;
};

export default RoleGuard;
