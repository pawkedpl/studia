# Paweł Kędzierski 272400

using LinearAlgebra

function gauss(A::Matrix{Float64}, size::Int64)::Float64
    x::Vector{Float64} = ones(Float64, size)
    b::Vector{Float64} = A * x;
    res::Vector{Float64} = A \ b
    ret::Float64 = norm((A \ b) - x) / norm(x)

    return ret
end

function inversion(A::Matrix{Float64}, size::Int64)::Float64
    x::Vector{Float64} = ones(Float64, size)
    b::Vector{Float64} = A * x;
    res::Vector{Float64} = inv(A) * b
    ret::Float64 = norm(res - x) / norm(x)

    return ret
end

println("\nTests for Hilbers, when n = {1, 2, ..., 20}: n --- condition --- rank --- gauss error --- inv error\n")

hil_range::Int64 = 20

for n::Int64 in 1:hil_range
    A::Matrix{Float64} = hilb(n) # println(typeof(A))
    println(n, " --- ", cond(A), " --- ", rank(A), " --- ", gauss(A, n), " --- ", inversion(A, n))
end

println("\nTests for random matrix, when n = {5, 10, 20} and c = {1, 10, 10^3, 10^7, 10^12, 10^16}:")
println("n --- c --- condition --- rank --- gauss error -- inv error\n")

gauss_range::Vector{Int64} = [5, 10, 20]
gauss_c::Vector{Int64} = [0, 1, 3, 7, 12, 16]

for n::Int64 in gauss_range
    for c::Int64 in gauss_c
        A::Matrix{Float64} = matcond(n, 10.0^c)
        println(n, " --- ", c, " --- ", cond(A), " --- ", rank(A), " --- ", gauss(A, n), " --- ", inversion(A, n))
    end
end