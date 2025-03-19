# Paweł Kędzierski 272400
# parametry funkcji:
#   x - wektor x
#   y - wektor y

function a(x::Vector{T}, y::Vector{T})::T where T <: AbstractFloat
    len::Int64 = length(x)
    S::T = zero(T)
    for i::Int64 in 1:len
        S += x[i] * y[i]
    end
    return S
end

# parametry funkcji:
#   x - wektor x
#   y - wektor y

function b(x::Vector{T}, y::Vector{T})::T where T <: AbstractFloat

    len::Int64 = length(x)
    S::T = zero(T)
    for i::Int64 in len:-1:1 
        S += x[i] * y[i]
    end
    return S
end

# parametry funkcji:
#   x - wektor x
#   y - wektor y

function c(x::Vector{T}, y::Vector{T})::T where T <: AbstractFloat


    len::Int64 = length(x)
    S::Vector{T} = Vector{T}(undef, len)

    for i::Int64 in 1:len
        S[i] = x[i] * y[i]
    end

    # vectorized dot operators
    S_pos::Vector{T} = S[S .>= zero(T)]
    S_neg::Vector{T} = S[S .< zero(T)]

    sort!(S_pos, rev=true)
    sort!(S_neg)
    sum_pos::T = zero(T)
    for i::Int64 in 1:length(S_pos)
        sum_pos += S_pos[i]
    end

    sum_neg::T = zero(T)
    for i::Int64 in 1:length(S_neg)
        sum_neg += S_neg[i]
    end

    return sum_pos + sum_neg
end

# parametry funkcji:
#   x - wektor x
#   y - wektor y

function d(x::Vector{T}, y::Vector{T})::T where T <: AbstractFloat


    len::Int64 = length(x)
    S::Vector{T} = Vector{T}(undef, len)

    for i::Int64 in 1:len
        S[i] = x[i] * y[i]
    end
    S_pos::Vector{T} = S[S .>= zero(T)]
    S_neg::Vector{T} = S[S .< zero(T)]
    # https://docs.julialang.org/en/v1/base/sort/
    sort!(S_pos)
    sort!(S_neg, rev=true)

    sum_pos::T = zero(T)
    for i::Int64 in 1:length(S_pos)
        sum_pos += S_pos[i]
    end

    sum_neg::T = zero(T)
    for i::Int64 in 1:length(S_neg)
        sum_neg += S_neg[i]
    end

    return sum_pos + sum_neg
end

x_32::Vector{Float32} = [2.718281828, −3.141592654, 1.414213562, 0.577215664, 0.301029995]
y_32::Vector{Float32} = [1486.2497, 878366.9879, −22.37492, 4773714.647, 0.000185049]

x_64::Vector{Float64} = [2.718281828, −3.141592654, 1.414213562, 0.577215664, 0.301029995]
y_64::Vector{Float64} = [1486.2497, 878366.9879, −22.37492, 4773714.647, 0.000185049]

x_32_old::Vector{Float32} = [2.718281828, −3.141592654, 1.414213562, 0.5772156649, 0.3010299957]
y_32_old::Vector{Float32} = [1486.2497, 878366.9879, −22.37492, 4773714.647, 0.000185049]

x_64_old::Vector{Float64} = [2.718281828, −3.141592654, 1.414213562, 0.5772156649, 0.3010299957]
y_64_old::Vector{Float64} = [1486.2497, 878366.9879, −22.37492, 4773714.647, 0.000185049]

println("For Float32: a --- b --- c --- d")
println(a(x_32, y_32), " --- ", b(x_32, y_32), " --- ", c(x_32, y_32), " --- ", d(x_32, y_32))
println("\nFor Float64: a --- b --- c --- d")
println(a(x_64, y_64), " --- ", b(x_64, y_64), " --- ", c(x_64, y_64), " --- ", d(x_64, y_64))

println("\nFor old data:")

println("\nFor Float32: a --- b --- c --- d")
println(a(x_32_old, y_32_old), " --- ", b(x_32_old, y_32_old), " --- ", c(x_32_old, y_32_old), " --- ", d(x_32_old, y_32_old))
println("\nFor Float64: a --- b --- c --- d")
println(a(x_64_old, y_64_old), " --- ", b(x_64_old, y_64_old), " --- ", c(x_64_old, y_64_old), " --- ", d(x_64_old, y_64_old))
