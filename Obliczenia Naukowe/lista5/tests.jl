# Paweł Kędzierski 272400

include("./blocksys.jl")
include("./IOMatrix.jl")
using .blocksys, .IOMatrix,  Test

using .blocksys: myMatrix


@testset "16 test - computeRightSideVector, gauss, gaussPivoted, luSolve, luSolvePivoted" begin
    ##########

    A= IOMatrix.readMatrix("test_data/16/A.txt")
    # println("Macierz ", A)
    b = IOMatrix.readVector("test_data/16/b.txt")
    # println("Wektor ", b)
    res::Vector{Float64} = IOMatrix.computeRightSideVector(A)
    # println("Wynik ", res)
    @test isapprox(res, b, rtol=0.1) #LOL 

    ##########
    
    @test isapprox(blocksys.gauss(A, b), \(A.matrix,b), rtol=0.1)

    ##########
    
    @test isapprox(blocksys.gaussPivoted(A, b), \(A.matrix,b), rtol=0.1)

    ##########
    
    @test isapprox(blocksys.luSolve(A, b), \(A.matrix,b), rtol=0.1)

    ##########

    @test isapprox(blocksys.luSolvePivoted(A, b), \(A.matrix,b), rtol=0.1)

end


