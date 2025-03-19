# Paweł Kędzierski 272400
using ForwardDiff

"""
Finds a root of a function using the method of bisection
    Arguments:
        f: input function f(x)
        a: beggining of an interval
        b: end of an interval
        delta: precision of r calculation
        epsilon: precision of f(r) calculation
    Returns:
        (r, w, it, err) a tuple of parameters
        r: found root
        w: f(r)
        it: number of iterations
        err: 0 if no errors occured, 1 otherwise
"""
function mbisekcji(f, a::Float64, b::Float64, delta::Float64, epsilon::Float64)

    e = b - a
    u = f(a)
    v = f(b)
    it = 0
    r = 0
    w = 0
    if sign(f(a)) == sign(f(b))
        return (r, w, it, 1)
    end
    
    while true
        it += 1
        e = e / 2
        r = (a + b) / 2
        w = f(r)

        if abs(e) < delta || abs(w) < epsilon
            return (r, w, it, 0)
        end
        if sign(w) != sign(u)
            b = r
            v = w
        else
            a = r
            u = w  
        end
    end
end

"""
Finds a root of a function using the Newton's method
    Arguments:
        f: input function f(x)
        f: derivative of the input function
        x0: initial approximation
        delta: precision of r calculation
        epsilon: precision of f(r) calculation
        maxit: maximum number of iterations
    Returns:
        (r, w, it, err) a tuple of parameters
        r: found root
        v: f(r)
        it: number of iterations
        err: 0 if no errors occured, 1 otherwise
"""
function mstycznych(f, pf, x0::Float64, delta::Float64, epsilon::Float64, maxit::Int)
    v = f(x0)
    if abs(v) < epsilon
        return (x0, v, 0, 1)
    end
    it = 0
    for it = 1:maxit
        if pf(x0) == 0
            return (x1, v, it, 2)
        end
        x1 = x0 - v / pf(x0)
        v = f(x1)
        if abs(x1 - x0) < delta || abs(v) < epsilon
            return (x1, v, it, 0)
        end
        x0 = x1
    end
    return (x1, v, it, 1)
end


"""
Finds a root of a function using a method of bisection
    Arguments:
        f: input function f(x)
        x0: initial approximation
        x1: initial approximation
        delta: precision of r calculation
        epsilon: precision of f(r) calculation
        maxit: maximum number of iterations
    Returns:
        (r, w, it, err) a tuple of parameters
        r: found root
        w: f(r)
        it: number of iterations
        err: 0 if no errors occured, 1 otherwise
"""
function msiecznych(f, a::Float64, b::Float64,
    delta::Float64, epsilon::Float64, maxit::Int)
    fa = f(a)
    fb = f(b)
    for it = 1:maxit
        if abs(fa) > abs(fb)
            temp = a
            a = b
            b = temp
            temp = fa
            fa = fb
            fb = temp
        end
        s = (b - a) / (fb - fa)
        b = a
        fb = fa
        a = a - fa * s
        fa = f(a)
        if(abs(b - a) < delta || abs(fa) < epsilon)
            return (a, fa, it, 0)
        end
    end
    return (a, fa, it, 1)
end

c1 = 3.6 * 10^9
nlogn(n) = n * log(2, n) - c1
println(mbisekcji(nlogn, 1.0, 1000000000.0, 0.001, 0.001))


# f4(x) = sin(x) - (x/2)^2
# pf4(x) = cos(x) - (x / 2)

# println("Zad 4:")
# println("r f(r) it err")
# println(mbisekcji(f4, 1.5, 2.0, 10^(-5) / 2, 10^(-5) / 2))
# println(mstycznych(f4, pf4, 1.5, 10^(-5) / 2, 10^(-5) / 2, 1000))
# println(msiecznych(f4, 1.0, 2.0, 10^(-5) / 2, 10^(-5) / 2, 1000))
# println()

f5(x) = 3* x - ℯ^x

#println("Zad 5:")
#println("r f(r) it err")
#println(mbisekcji(f5, 1.0, 2.0, 10^(-5), 10^(-5)))
#println()
println("Zad 6:")

delta::Float64 = 10^(-5)
epsilon::Float64 = 10^(-5)

f1(x) = exp(1-x) - 1
f2(x) = x*exp(-x)

pf1(x) = -exp(1-x)
pf2(x) = -exp(-x) * (x-1)

maxit::Int = 100

a1::Float64 = 0.0
b1::Float64 = 1.0

x0_1::Float64 = 0.0

x1_1::Float64 = 0.5


println("\nDla 1. funkcji:")
println("\nMetoda bisekcji dla a = ", a1," i b = ", b1, ":")
println(mbisekcji(f1, a1, b1, delta, epsilon))

println("\nMetoda Newtona dla x0 = ", x0_1, ":")
println(mstycznych(f1, pf1, x0_1, delta, epsilon, maxit))

println("\nMetoda siecznych dla x0 = ", x0_1, " i x1 = ", x1_1, ":")
println(msiecznych(f1, x0_1, x1_1, delta, epsilon, maxit))

x0_1 = -1.0

x1_1 = -0.5

println("\nDla 2. funkcji:")
println("\nMetoda bisekcji dla a = ", a1," i b = ", b1, ":")
println(mbisekcji(f2, a1, b1, delta, epsilon))

println("\nMetoda Newtona dla x0 = ", x0_1, ":")
println(mstycznych(f2, pf2, x0_1, delta, epsilon, maxit))

println("\nMetoda siecznych dla x0 = ", x0_1, " i x1 = ", x1_1, ":")
println(msiecznych(f2, x0_1, x1_1, delta, epsilon, maxit))


