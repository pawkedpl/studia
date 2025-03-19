# Paweł Kędzierski 272400
#
# modul blocksys, w ktorym znajduja sie implementacje funkcji dzialajacych na macierzach

__precompile__()

module blocksys
include("./IOMatrix.jl")
using .IOMatrix: myMatrix
using SparseArrays
export gauss, gaussPivoted, lu, luPivoted, luSolve, luSolvePivoted


# rozwiazywanie Ax = b metoda gaussa bez wyboru elementu glownego
# param: macierz myMatrix, wektor b 
# return: wektor x
function gauss(A, b::Vector{Float64})::Vector{Float64}

    for i::Int in 1:A.size-1
        l_col::Int64 = min(i + A.block_size, A.size)
        l_row::Int64 = min(A.size, A.block_size + A.block_size * floor(Int64, i/A.block_size))

        for j::Int in i+1:l_row
            z = A.matrix[j,i] / A.matrix[i,i]
            A.matrix[j,i] = 0

            for k::Int in i + 1:l_col
                A.matrix[j, k] -= z * A.matrix[i, k]
            end

            b[j] -= z * b[i]
        end
    end

    x::Vector{Float64} = zeros(A.size)

    for i in A.size:-1:1 
        sum::Float64 = 0.0;
        l_col = min(A.size, i + A.block_size)

        for j::Int in i+1:l_col 
            sum += A.matrix[i, j]*x[j] 
        end

        x[i] = (b[i] - sum) / A.matrix[i,i]
    end

    return x
end

# rozwiazywanie Ax = b metoda gaussa z wyborem elementu glownego  
# param: macierz myMatrix, wektor b 
# return: wektor x
function gaussPivoted(A, b::Vector{Float64})::Vector{Float64}
    perm = collect(1:A.size)

    for i in 1:A.size-1
        l_col = min(i + A.block_size, A.size)
        l_row = min(A.size, A.block_size + A.block_size * floor(Int, i / A.block_size))

        max_idx = i
        max_val = abs(A.matrix[perm[i], i])

        for k in i+1:l_row
            val = abs(A.matrix[perm[k], i])
            if val > max_val
                max_idx, max_val = k, val
            end
        end

        perm[i], perm[max_idx] = perm[max_idx], perm[i]

        for j in i+1:l_row
            z = A.matrix[perm[j], i] / A.matrix[perm[i], i]
            A.matrix[perm[j], i] = 0

            for k in i+1:l_col
                A.matrix[perm[j], k] -= z * A.matrix[perm[i], k]
            end

            b[perm[j]] -= z * b[perm[i]]
        end
    end

    x = zeros(Float64, A.size)
    for i in A.size:-1:1
        sum = 0.0
        l_col = min(A.size, i + A.block_size)

        for j in i+1:l_col
            sum += A.matrix[perm[i], j] * x[j]
        end

        x[i] = (b[perm[i]] - sum) / A.matrix[perm[i], i]
    end

    return x

end

# wyznaczanie rozkladu LU metoda eliminacji gaussa bez wyboru elementu glownego
# param: myMatrix
# ret: myMatrix ale po LU
function lu(A::myMatrix)::Nothing
    # gauss ale lekka modyfikacja
    for i::Int in 1:A.size-1
        l_col::Int64 = min(i + A.block_size, A.size)
        l_row::Int64 = min(A.size, A.block_size + A.block_size * floor(Int64, i/A.block_size))

        for j::Int in i+1:l_row
            z = A.matrix[j,i] / A.matrix[i,i]
            A.matrix[j,i] = z

            for k::Int in i + 1:l_col
                A.matrix[j, k] -= z * A.matrix[i, k]
            end
        end
    end
end

# wyznaczanie rozkladu LU metoda eliminacji gaussa z wyborem elementu glownego
# param: myMatrix
# ret: myMatrix ale po LU
function luPivoted(A::myMatrix)::Nothing
    # pivoted gauss ale lekka modyfikacja
    perm = collect(1:A.size)

    for i in 1:A.size-1
        l_col = min(i + A.block_size, A.size)
        l_row = min(A.size, A.block_size + A.block_size * floor(Int, i / A.block_size))

        max_idx = i
        max_val = abs(A.matrix[perm[i], i])

        for k in i+1:l_row
            val = abs(A.matrix[perm[k], i])
            if val > max_val
                max_idx, max_val = k, val
            end
        end

        perm[i], perm[max_idx] = perm[max_idx], perm[i]

        for j in i+1:l_row
            z = A.matrix[perm[j], i] / A.matrix[perm[i], i]
            A.matrix[perm[j], i] = z

            for k in i+1:l_col
                A.matrix[perm[j], k] -= z * A.matrix[perm[i], k]
            end
        end
    end
end

# rozwiazywanie ukladu rownan Ax = b po wczesniejszym wyznaczeniu rozkladu LU 
# param: myMatrix, wektor b 
# ret: wektor x
function luSolve(A, b::Vector{Float64})::Vector{Float64}
     # gauss ale lekka modyfikacja
    for i::Int in 1:A.size-1
        l_col::Int64 = min(i + A.block_size, A.size)
        l_row::Int64 = min(A.size, A.block_size + A.block_size * floor(i/A.block_size))

        for j::Int in i+1:l_row
            z = A.matrix[j,i] / A.matrix[i,i]
            A.matrix[j,i] = z

            for k::Int in i + 1:l_col
                A.matrix[j, k] -= z * A.matrix[i, k]
            end
        end
    end


    x = zeros(Float64, A.size)

    for i in 1:A.size
        sum = 0.0
        for j in max(1, floor(Int, (i - 1) / A.block_size) * A.block_size):i-1
            sum += A.matrix[i, j] * x[j]
        end

        x[i] = (b[i] - sum) / A.matrix[i, i]
    end

    for i in A.size:-1:1
        sum = 0.0
        l_col = min(A.size, i + A.block_size)

        for j in i+1:l_col
            sum += A.matrix[i, j] * x[j]
        end

        x[i] = (b[i] - sum) / A.matrix[i, i]
    end

    return x
end

# rozwiazywanie ukladu rownan Ax = b po wczesniejszym wyznaczeniu rozkladu LU przy uzyciu pivoted gauss 
# param: myMatrix, wektor b 
# ret: wektor x
function luSolvePivoted(A, b::Vector{Float64})::Vector{Float64}
    perm = collect(1:A.size)

    for i in 1:A.size-1
        l_col = min(i + A.block_size, A.size)
        l_row = min(A.size, A.block_size + A.block_size * floor(Int, i / A.block_size))

        max_idx = i
        max_val = abs(A.matrix[perm[i], i])

        for k in i+1:l_row
            val = abs(A.matrix[perm[k], i])
            if val > max_val
                max_idx, max_val = k, val
            end
        end

        perm[i], perm[max_idx] = perm[max_idx], perm[i]

        for j in i+1:l_row
            z = A.matrix[perm[j], i] / A.matrix[perm[i], i]
            A.matrix[perm[j], i] = z

            for k in i+1:l_col
                A.matrix[perm[j], k] -= z * A.matrix[perm[i], k]
            end
        end
    end

    bperm = zeros(A.size)
    for i in 1 : A.size
	bperm[i] = b[perm[i]]
    end

    y = zeros(A.size)
    for i in 1:A.size
        sum = 0.0
        for j in max(1, floor(Int, (i - 1) / A.block_size) * A.block_size):i-1
            sum += A.matrix[i, j] * y[j]
        end

        y[i] = (bperm[i] - sum) / A.matrix[i, i]
    end

    x = zeros(A.size)
    for i in A.size:-1:1
        sum = 0.0
        l_col = min(A.size, i + A.block_size)

        for j in i+1:l_col
            sum += A.matrix[i, j] * x[j]
        end

        x[i] = (b[i] - sum) / A.matrix[i, i]
    end

    return x
end

end
