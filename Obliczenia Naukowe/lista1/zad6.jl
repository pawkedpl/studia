# Pawel Kedzierski 272400

# parametry funkcji:
#   x - wartość argumentu x
#   T - typ zmiennoprzecinkowy

function f(x, T)
    return sqrt(x^2 + one(T)) - one(T)
end

function g(x, T)
    return x^2 / ( sqrt(x^2 + one(T)) + one(T) )
end

x::Float64 = 8.0
for p in 1:10
    println("f(", x, "^-", p, "): ", f(x^(-p), Float64))
    println("g(", x, "^-", p, "): ", g(x^(-p), Float64))
    println("\n")
end