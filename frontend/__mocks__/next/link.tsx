import React from 'react';

const Link = ({ href, children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) =>
  React.createElement('a', { href, ...props }, children);

export default Link;
