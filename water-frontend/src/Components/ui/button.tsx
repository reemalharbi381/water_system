export const Button = ({ children, className, ...props }: any) => (
  <button className={`px-4 py-2 rounded-xl font-bold transition-all ${className}`} {...props}>
    {children}
  </button>
);